from gpiozero import AngularServo
from gpiozero.pins.lgpio import LGPIOFactory
from time import sleep

# Use lgpio for Raspberry Pi 5
factory = LGPIOFactory()

servo = AngularServo(
    14,
    min_angle=0,
    max_angle=120,
    min_pulse_width=0.5/1000,
    max_pulse_width=2.5/1000,
    pin_factory=factory
)

# Define angles
a = 100
b = 70

# Repeat 10 times
for _ in range(10):

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

print("Done")