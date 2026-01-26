import time
from gpiozero import Servo
from rc_pwm import RcPwmReader

SERVO_PIN = 21  # BCM21 (werkt bij jou in testscript)
SERVO = Servo(SERVO_PIN, min_pulse_width=0.0005, max_pulse_width=0.0025)

with RcPwmReader({"steer": 22, "throttle": 27}, failsafe_s=0.25) as rx:
    while True:
        steer = rx.read("steer")

        if steer.norm is None:
            SERVO.value = 0.0  # center on failsafe
        else:
            SERVO.value = steer.norm  # -1..+1 direct

        time.sleep(0.02)  # 50Hz