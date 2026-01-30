import time
import board
import busio
from adafruit_pca9685 import PCA9685

# I2C setup
i2c = busio.I2C(board.SCL, board.SDA)

# PCA9685 init
pca = PCA9685(i2c)
pca.frequency = 50  # Servo frequency

# Channel 0 (servo)
servo = pca.channels[0]

def angle_to_pwm(angle):
    # 0° → ~500µs, 180° → ~2500µs
    pulse_min = 500
    pulse_max = 2500
    pulse = pulse_min + (pulse_max - pulse_min) * angle / 180
    return int(pulse * 65535 / 20000)  # 20ms period

try:
    while True:
        servo.duty_cycle = angle_to_pwm(0)
        time.sleep(1)
        servo.duty_cycle = angle_to_pwm(90)
        time.sleep(1)
        servo.duty_cycle = angle_to_pwm(180)
        time.sleep(1)

except KeyboardInterrupt:
    servo.duty_cycle = angle_to_pwm(90)
    time.sleep(1)
    pca.deinit()