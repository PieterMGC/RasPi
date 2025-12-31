from gpiozero import Servo
from time import sleep
from gpiozero.pins.lgpio import LGPIOFactory

factory = LGPIOFactory()
servo = Servo(21, pin_factory=factory)

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