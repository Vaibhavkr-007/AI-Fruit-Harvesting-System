from gpiozero import AngularServo
from gpiozero.pins.lgpio import LGPIOFactory
from time import sleep

factory = LGPIOFactory()

servo = AngularServo(
    14,
    min_angle=0,
    max_angle=120,
    pin_factory=factory
)

while True:
    servo.angle = 50
    sleep(1)

    servo.angle = 70
    sleep(1)

    servo.angle = 100
    sleep(1)