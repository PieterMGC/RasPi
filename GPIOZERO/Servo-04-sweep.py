from gpiozero import Servo
from time import sleep
import math
from gpiozero.pins.lgpio import LGPIOFactory

factory = LGPIOFactory()
servo = Servo(4, min_pulse_width = 0.5/1000, max_pulse_width = 2.5/1000,pin_factory=factory)

while True:
    for i in range (0, 360):
        servo.value = math.sin(math.radians(i))
        sleep(0.01)