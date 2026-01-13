#wiring: see Lafvin starter kit manual

from gpiozero import Motor
from time import sleep

# BCM pin numbers
motor = Motor(forward=27, backward=17, enable=18, pwm=True)

try:
    motor.forward(0.6)   # 60% speed
    sleep(2)

    motor.stop()
    sleep(0.5)

    motor.backward(0.6)
    sleep(2)

finally:
    motor.stop()