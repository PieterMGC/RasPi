from gpiozero import Servo
from time import sleep

SERVO_PIN = 21  # <-- zet op 9 als je servo op fysieke pin 21 zit

s = Servo(SERVO_PIN, min_pulse_width=0.0005, max_pulse_width=0.0025)

while True:
    s.value = -1
    sleep(1)
    s.value = 0
    sleep(1)
    s.value = 1
    sleep(1)