# 🚁 Autonomous Quadcopter Drone for Fruit Harvesting Assistance

![Project Status](https://img.shields.io/badge/Status-Prototype_Completed-success)
![Platform](https://img.shields.io/badge/Platform-Raspberry_Pi_5-C51A4A?logo=raspberrypi)
![AI](https://img.shields.io/badge/AI_Model-YOLOv11_NCNN-00FFFF?logo=pytorch)
![CAD](https://img.shields.io/badge/CAD-Fusion_360-0696D7?logo=autodesk)

> 💡 **How to add your images to this README:** > Create a folder named `assets` in your GitHub repository, upload your project photos (like your CAD renders, YOLO detections, or the final physical drone), and ensure the file names match the paths in the placeholders below (e.g., `![Alt Text](assets/image_name.png)`).

## 📖 Overview

This repository contains the design, code, and manufacturing details of an autonomous quadcopter drone engineered to assist in fruit harvesting. Developed to tackle agricultural labor shortages and mitigate the physical risks of manual harvesting, this drone integrates aerial mobility with advanced computer vision and a custom 3D-printed mechanical harvesting system.

By leveraging an onboard **Raspberry Pi 5** and the **YOLOv11** object detection architecture (optimized with NCNN), the drone can autonomously navigate to the tree canopy, identify ripe fruits (apples, mangoes, oranges), calculate distances dynamically, and harvest them using a custom scissor-mechanism.

![Drone Assembly](assets/drone_assembly.png)
*Replace this with a photo of your final quadcopter assembly.*

---

## ✨ Key Innovations

1. **📏 Extended Harvesting Arm:** A ~480mm lightweight, rigid support rod made from PETG Pro that keeps the drone's propellers at a safe distance from branches while reaching into the canopy.
2. **✂️ Scissor-Type Cutting Mechanism:** A servo-actuated end-effector mounted at the tip of the extended arm that precisely severs the fruit stem once alignment is confirmed.
3. **🧺 V-Shaped Collection Container:** A foldable, bottom-mounted compartment that safely catches the harvested fruit and transports it to a designated collection bin.
4. **🧠 AI-Driven Ripeness & Distance Detection:** Analyzes bounding box color for ripeness and utilizes bounding box diameter alongside camera focal length to calculate real-time distance.

---

## 💻 Codebase Structure

The software side of the project is split into two primary modules:

* `servo/`: Contains test scripts specifically for validating and calibrating the servo motor that drives the scissor cutting mechanism.
* `yolo_detect/`: Contains the core computer vision pipeline. This includes the highly optimized NCNN format YOLO model and the `yolo_detect.py` script, which handles real-time inference, ripeness classification, and distance estimation.

---

## 🚀 Getting Started & Usage

### 1. Hardware Prerequisites
* Raspberry Pi 5 with Pi Camera Module v3 (or equivalent) mounted.
* Tarot Ironman 650 Quadcopter frame fully assembled with the flight controller (RadioLink CrossFlight).
* Servo motor wired correctly to the Pi's GPIO/companion setup.

### 2. Environment Setup

It is highly recommended to run the code inside a Python Virtual Environment to prevent dependency conflicts on the Raspberry Pi.

Open your terminal and run the following commands:

```bash
# Clone the repository
git clone https://github.com/Vaibhavkr-007/AI-Fruit-Harvesting-System.git
cd AI-Fruit-Harvesting-System

# Create a virtual environment named 'venv'
python -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install the required dependencies
pip install -r requirements.txt
```

### 3. Testing the Servo Mechanism

Before flight, ensure your cutting mechanism operates smoothly:

```bash
cd servo
# Run the servo test script (replace with your actual script name)
python test_servo.py
```

### 4. Running the Vision & Distance Model

Navigate to the vision directory to run the optimized YOLO detection script. The script takes the NCNN model, grabs the camera feed, and calculates the distance to the apple using its bounding box diameter and the camera's focal length.

```bash
cd ../yolo_detect

# Run the detection model
python yolo_detect.py --model=best_ncnn_model --source=picamera0 --resolution=1280x720
```

*Note: The `--source=picamera0` flag targets the default Raspberry Pi camera interface.*

---

## 🛠️ Hardware & Technical Specifications

| Specification | Value | Description |
| :--- | :--- | :--- |
| **Total Weight (incl. Payload)** | 9.0 Kg | Includes frame, motors, battery, and a 2.5 Kg fruit payload capacity |
| **Battery** | 10,000mAh 6S LiPo | Powers the flight controller, Pi 5, and harvesting servo |
| **Flight Controller** | RadioLink CrossFlight | Manages low-level stabilization and telemetry |
| **Companion Computer** | Raspberry Pi 5 | Runs real-time YOLOv11 NCNN inference |
| **Thrust-to-Weight Ratio** | 2.18 : 1 | Ensures high maneuverability and heavy-lifting capability |

![CAD Model Dimensions](assets/cad_dimensions.png)
*Replace this with your CAD design drawing.*

---

## 🏗️ Mechanical & Structural Engineering

Extensive simulations were conducted in **SolidWorks** to validate the mechanical integrity of the 3D-printed payload components. 

* **Static Structural Stress Analysis:** Verified that the extended PETG Pro arm safely supports the bending moments generated by the cutting action and payload. Maximum stress remained well below the material's yield strength.
* **Frequency (Modal) Analysis:** Confirmed that the first natural frequency of the arm (10.506 Hz) does not resonate with the operational vibrations generated by the motors.
* **Static Balancing:** The heavy 6S LiPo battery was shifted to the rear of the drone to perfectly counterbalance the forward center of gravity (CG) shift.

![Static Stress Analysis](assets/stress_analysis.png)
*Replace this with your SolidWorks simulation snippet.*

---

## 👥 Contributors

This research and development project was executed by a collaborative engineering group from the Mechanical Engineering Department at the National Institute of Technology Hamirpur (Batch 2022-2026), under the supervision of Prof. Rakesh Sehgal.

* **Abhishek Kashyap** (22BME008)
* **Akash Kanwar** (22BME014)
* **Aryan Raghuvanshi** (22BME030)
* **Vaibhav Kumar Mahto** (22BME116)