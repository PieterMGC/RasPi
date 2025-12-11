from adafruit_servokit import ServoKit
from time import sleep

# PCA9685 on the Pan-Tilt HAT has 16 channels
kit = ServoKit(channels=16)

# Waveshare servos are typical hobby servos, start with 500–2500 µs range
kit.servo[0].set_pulse_width_range(500, 2500)  # tilt  (S0)
kit.servo[1].set_pulse_width_range(500, 2500)  # pan   (S1)

def center_all():
    kit.servo[0].angle = 90  # center tilt
    kit.servo[1].angle = 90  # center pan

center_all()
print("Servos moved to center (90°). Leave them here while you mount the mechanics.")
