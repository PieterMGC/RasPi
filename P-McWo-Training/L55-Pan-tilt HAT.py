from adafruit_servokit import ServoKit
from time import sleep

kit = ServoKit(channels=16)

# Tune per your hardware
kit.servo[0].set_pulse_width_range(500, 2500)  # tilt
kit.servo[1].set_pulse_width_range(500, 2500)  # pan

TILT = 0
PAN = 1

# Safe movement limits
PAN_MIN, PAN_MAX = 40, 140
TILT_MIN, TILT_MAX = 60, 120

def goto(pan_angle, tilt_angle, pause=0.3):
    kit.servo[PAN].angle = pan_angle
    kit.servo[TILT].angle = tilt_angle
    sleep(pause)

def smooth_move(channel, target, step=1, delay=0.01):
    current = kit.servo[channel].angle
    if current is None:
        current = target
    direction = step if target > current else -step

    for a in range(int(current), int(target), direction):
        kit.servo[channel].angle = a
        sleep(delay)

    kit.servo[channel].angle = target


try:
    # start centered
    goto(90, 90, 1)

    while True:
        # Smooth pan sweep
        smooth_move(PAN, PAN_MAX)
        smooth_move(PAN, PAN_MIN)

        # Smooth tilt nod
        smooth_move(TILT, TILT_MAX)
        smooth_move(TILT, TILT_MIN)

except KeyboardInterrupt:
    goto(90, 90, 0.5)
    print("Stopped and centered.")