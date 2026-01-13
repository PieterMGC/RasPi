from gpiozero import Servo
from time import sleep

servo = Servo(4)

print("Middle")
servo.mid()
sleep(5)
print("Min")
servo.min()
sleep(5)
print("Max")
servo.max()
sleep(5)
print("Middle")
servo.mid()
sleep(5)
servo.value = none