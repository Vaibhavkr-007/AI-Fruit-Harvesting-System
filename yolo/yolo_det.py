import os
import sys
import argparse
import glob
import time

import cv2
import numpy as np
from ultralytics import YOLO

# --- ADDED SERVO IMPORTS ---
from gpiozero import AngularServo
from gpiozero.pins.lgpio import LGPIOFactory
from time import sleep

# --- ADDED CONSTANTS FOR DISTANCE ESTIMATION ---
KNOWN_APPLE_DIAMETER_CM = 5.0 
FOCAL_LENGTH = 1800.0  # Replace this with your calibrated value

# --- ADDED CONSTANTS FOR SCISSOR TRIGGER ---
TARGET_DISTANCE = 58.0
DISTANCE_TOLERANCE = 2.0 # Allows activation between 56cm and 60cm
TARGET_Y1 = 0.333
TARGET_Y2 = 0.611
TARGET_X1 = 0.071
TARGET_X2 = 0.357

# --- SERVO SETUP ---
# Use lgpio for Raspberry Pi 5
factory = LGPIOFactory()
servo = AngularServo(
    14,
    min_angle=0,
    max_angle=120,
    min_pulse_width=5/1000,
    max_pulse_width=7/1000,
    pin_factory=factory
)

def activate_scissor():
    """Executes the servo motor sequence twice."""
    print("Apple in target zone and distance! Activating scissor mechanism...")
    a = 100
    b = 70
    
    # Repeat 2 times as requested
    for _ in range(2):
        # Move slowly from a to b
        step = -1 if a > b else 1
        for angle in range(a, b + step, step):
            servo.angle = angle
            sleep(0.05)

        # Move slowly from b to a
        step = -1 if b > a else 1
        for angle in range(b, a + step, step):
            servo.angle = angle
            sleep(0.05)
    print("Scissor mechanism done.")
# -------------------

# Define and parse user input arguments
parser = argparse.ArgumentParser()
parser.add_argument('--model', help='Path to YOLO model file (example: "runs/detect/train/weights/best.pt")',
                    required=True)
parser.add_argument('--source', help='Image source, can be image file ("test.jpg"), image folder ("test_dir"), video file ("testvid.mp4"), or index of USB camera ("usb0")', 
                    required=True)
parser.add_argument('--thresh', help='Minimum confidence threshold for displaying detected objects (example: "0.4")',
                    default=0.5)
parser.add_argument('--resolution', help='Resolution in WxH to display inference results at (example: "640x480"), otherwise, match source resolution',
                    default=None)
parser.add_argument('--record', help='Record results from video or webcam and save it as "demo1.avi". Must specify --resolution argument to record.',
                    action='store_true')

args = parser.parse_args()

# Parse user inputs
model_path = args.model
img_source = args.source
min_thresh = float(args.thresh)
user_res = args.resolution
record = args.record

# Check if model file exists and is valid
if not os.path.exists(model_path):
    print('ERROR: Model path is invalid or model was not found. Make sure the model filename was entered correctly.')
    sys.exit(0)

# Load the model into memory and get label map
model = YOLO(model_path, task='detect')
labels = model.names

# Parse input to determine if image source is a file, folder, video, or USB camera
img_ext_list = ['.jpg','.JPG','.jpeg','.JPEG','.png','.PNG','.bmp','.BMP']
vid_ext_list = ['.avi','.mov','.mp4','.mkv','.wmv']

if os.path.isdir(img_source):
    source_type = 'folder'
elif os.path.isfile(img_source):
    _, ext = os.path.splitext(img_source)
    if ext in img_ext_list:
        source_type = 'image'
    elif ext in vid_ext_list:
        source_type = 'video'
    else:
        print(f'File extension {ext} is not supported.')
        sys.exit(0)
elif 'usb' in img_source:
    source_type = 'usb'
    usb_idx = int(img_source[3:])
elif 'picamera' in img_source:
    source_type = 'picamera'
    picam_idx = int(img_source[8:])
else:
    print(f'Input {img_source} is invalid. Please try again.')
    sys.exit(0)

# Parse user-specified display resolution
resize = False
if user_res:
    resize = True
    resW, resH = int(user_res.split('x')[0]), int(user_res.split('x')[1])

# Check if recording is valid and set up recording
if record:
    if source_type not in ['video','usb']:
        print('Recording only works for video and camera sources. Please try again.')
        sys.exit(0)
    if not user_res:
        print('Please specify resolution to record video at.')
        sys.exit(0)
    
    # Set up recording
    record_name = 'demo1.avi'
    record_fps = 30
    recorder = cv2.VideoWriter(record_name, cv2.VideoWriter_fourcc(*'MJPG'), record_fps, (resW,resH))

# Load or initialize image source
if source_type == 'image':
    imgs_list = [img_source]
elif source_type == 'folder':
    imgs_list = []
    filelist = glob.glob(img_source + '/*')
    for file in filelist:
        _, file_ext = os.path.splitext(file)
        if file_ext in img_ext_list:
            imgs_list.append(file)
elif source_type == 'video' or source_type == 'usb':
    if source_type == 'video': cap_arg = img_source
    elif source_type == 'usb': cap_arg = usb_idx
    cap = cv2.VideoCapture(cap_arg)

    # Set camera or video resolution if specified by user
    if user_res:
        ret = cap.set(3, resW)
        ret = cap.set(4, resH)

elif source_type == 'picamera':
    from picamera2 import Picamera2
    cap = Picamera2()
    cap.configure(cap.create_video_configuration(main={"format": 'XRGB8888', "size": (resW, resH)}))
    cap.start()

# Set bounding box colors (using the Tableu 10 color scheme)
bbox_colors = [(164,120,87), (68,148,228), (93,97,209), (178,182,133), (88,159,106), 
               (96,202,231), (159,124,168), (169,162,241), (98,118,150), (172,176,184)]

# Initialize control and status variables
avg_frame_rate = 0
frame_rate_buffer = []
fps_avg_len = 200
img_count = 0

# Begin inference loop
while True:

    t_start = time.perf_counter()

    # Load frame from image source
    if source_type == 'image' or source_type == 'folder': 
        if img_count >= len(imgs_list):
            print('All images have been processed. Exiting program.')
            sys.exit(0)
        img_filename = imgs_list[img_count]
        frame = cv2.imread(img_filename)
        img_count = img_count + 1
    
    elif source_type == 'video': 
        ret, frame = cap.read()
        if not ret:
            print('Reached end of the video file. Exiting program.')
            break
    
    elif source_type == 'usb': 
        ret, frame = cap.read()
        if (frame is None) or (not ret):
            print('Unable to read frames from the camera. This indicates the camera is disconnected or not working. Exiting program.')
            break

    elif source_type == 'picamera': 
        frame_bgra = cap.capture_array()
        frame = cv2.cvtColor(np.copy(frame_bgra), cv2.COLOR_BGRA2BGR)
        if (frame is None):
            print('Unable to read frames from the Picamera. This indicates the camera is disconnected or not working. Exiting program.')
            break

    # Resize frame to desired display resolution
    if resize == True:
        frame = cv2.resize(frame,(resW,resH))
        
    frame_h, frame_w = frame.shape[:2]

    # Run inference on frame
    results = model(frame, verbose=False)

    # Extract results
    detections = results[0].boxes

    # Initialize variable for basic object counting example
    object_count = 0

    # Go through each detection and get bbox coords, confidence, and class
    for i in range(len(detections)):

        # Get bounding box coordinates
        xyxy_tensor = detections[i].xyxy.cpu() 
        xyxy = xyxy_tensor.numpy().squeeze() 
        xmin, ymin, xmax, ymax = xyxy.astype(int) 

        # Get bounding box class ID and name
        classidx = int(detections[i].cls.item())
        classname = labels[classidx]

        # Get bounding box confidence
        conf = detections[i].conf.item()

        # Draw box if confidence threshold is high enough
        if conf > min_thresh:

            color = bbox_colors[classidx % 10]
            cv2.rectangle(frame, (xmin,ymin), (xmax,ymax), color, 2)

            # --- DISTANCE ESTIMATION LOGIC ---
            if classname.lower() == 'apple':
                # Apples are roughly spherical, so we take the max of width/height as the diameter in pixels
                pixel_width = xmax - xmin
                pixel_height = ymax - ymin
                pixel_diameter = max(pixel_width, pixel_height)
                
                if pixel_diameter > 0:
                    # Apply triangle similarity formula: Distance = (Real Width * Focal Length) / Pixel Width
                    distance_cm = (KNOWN_APPLE_DIAMETER_CM * FOCAL_LENGTH) / pixel_diameter
                    label = f'{classname}: {int(conf*100)}% | Dist: {distance_cm:.1f}cm'
                    
                    # --- ADDED TARGET CHECK & SCISSOR EXECUTION ---
                    # 1. Check distance with tolerance
                    if abs(distance_cm - TARGET_DISTANCE) <= DISTANCE_TOLERANCE:
                        # 2. Check normalized coordinates of the apple's center
                        cx = (xmin + xmax) / 2.0
                        cy = (ymin + ymax) / 2.0
                        norm_x = cx / frame_w
                        norm_y = cy / frame_h
                        
                        if (TARGET_X1 <= norm_x <= TARGET_X2) and (TARGET_Y1 <= norm_y <= TARGET_Y2):
                            # Provide visual feedback on frame
                            cv2.putText(frame, "SCISSOR ACTIVATED!", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
                            cv2.imshow('YOLO detection results', frame)
                            cv2.waitKey(1) # Force frame update before blocking for servo
                            
                            # Execute Servo
                            activate_scissor()
                    # ----------------------------------------------
                else:
                    label = f'{classname}: {int(conf*100)}%'
            else:
                label = f'{classname}: {int(conf*100)}%'
            # ---------------------------------

            labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1) 
            label_ymin = max(ymin, labelSize[1] + 10) 
            cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), color, cv2.FILLED) 
            cv2.putText(frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1) 

            # Basic example: count the number of objects in the image
            object_count = object_count + 1
            
    # Optional: Draw the target area on the frame for debugging (can be commented out)
    target_xmin = int(TARGET_X1 * frame_w)
    target_xmax = int(TARGET_X2 * frame_w)
    target_ymin = int(TARGET_Y1 * frame_h)
    target_ymax = int(TARGET_Y2 * frame_h)
    cv2.rectangle(frame, (target_xmin, target_ymin), (target_xmax, target_ymax), (0, 255, 0), 1)

    # Calculate and draw framerate (if using video, USB, or Picamera source)
    if source_type in ['video', 'usb', 'picamera']:
        cv2.putText(frame, f'FPS: {avg_frame_rate:0.2f}', (10,20), cv2.FONT_HERSHEY_SIMPLEX, .7, (0,255,255), 2) 
    
    # Display detection results
    cv2.putText(frame, f'Number of objects: {object_count}', (10,40), cv2.FONT_HERSHEY_SIMPLEX, .7, (0,255,255), 2) 
    cv2.imshow('YOLO detection results', frame) 
    if record: recorder.write(frame)

    # If inferencing on individual images, wait for user keypress before moving to next image. 
    # Otherwise, wait 5ms before moving to next frame.
    if source_type == 'image' or source_type == 'folder':
        key = cv2.waitKey()
    else:
        key = cv2.waitKey(5)
    
    if key == ord('q') or key == ord('Q'): # Press 'q' to quit
        break
    elif key == ord('s') or key == ord('S'): # Press 's' to pause inference
        cv2.waitKey()
    elif key == ord('p') or key == ord('P'): # Press 'p' to save a picture of results on this frame
        cv2.imwrite('capture.png', frame)
    
    # Calculate FPS for this frame
    t_stop = time.perf_counter()
    frame_rate_calc = float(1/(t_stop - t_start))

    # Append FPS result to frame_rate_buffer (for finding average FPS over multiple frames)
    if len(frame_rate_buffer) >= fps_avg_len:
        temp = frame_rate_buffer.pop(0)
        frame_rate_buffer.append(frame_rate_calc)
    else:
        frame_rate_buffer.append(frame_rate_calc)

    # Calculate average FPS for past frames
    avg_frame_rate = np.mean(frame_rate_buffer)

# Clean up
print(f'Average pipeline FPS: {avg_frame_rate:.2f}')
if source_type == 'video' or source_type == 'usb':
    cap.release()
elif source_type == 'picamera':
    cap.stop()
if record: recorder.release()
cv2.destroyAllWindows()