from gpiozero import AngularServo
from time import sleep

servo = AngularServo(4, min_angle=0, max_angle=100)

while True:
    servo.angle = 0
    sleep(2)
    servo.angle = 25
    sleep(2)
    servo.angle = 50
    sleep(2)
    servo.angle = 75
    sleep(2)
    servo.angle = 100
    sleep(2)