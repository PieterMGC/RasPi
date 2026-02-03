import time
import board
import busio
from adafruit_pca9685 import PCA9685

from rc_pwm import RcPwmReader

# --- Receiver input GPIOs (BCM) ---
CH1_STEER_PIN = 22

# --- PCA9685 settings ---
PCA9685_ADDR = 0x40     # default
SERVO_CH = 0            # channel on PCA9685
SERVO_FREQ = 50         # Hz

# Limit to ~180° (safe range for most servos)
SERVO_MIN_US = 1000
SERVO_MAX_US = 2000
SERVO_TRIM_US = 0       # +/- microseconds to center

# Optional: reduce tiny twitch around center
STEER_DEADBAND = 0.02

def us_to_duty(us: float) -> int:
    """Convert pulse width (us) to PCA9685 16-bit duty_cycle at SERVO_FREQ."""
    period_us = 1_000_000.0 / SERVO_FREQ  # 20,000 us at 50Hz
    return int((us / period_us) * 65535)

def set_servo_norm(channel, norm):
    """
    norm: -1..+1 or None
    """
    if norm is None:
        norm = 0.0

    norm = float(max(-1.0, min(1.0, norm)))
    if abs(norm) < STEER_DEADBAND:
        norm = 0.0

    mid = (SERVO_MIN_US + SERVO_MAX_US) / 2.0 + SERVO_TRIM_US
    span = (SERVO_MAX_US - SERVO_MIN_US) / 2.0

    us = mid + (norm * span)
    us = max(SERVO_MIN_US, min(SERVO_MAX_US, us))

    channel.duty_cycle = us_to_duty(us)

print("Init PCA9685...")
i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c, address=PCA9685_ADDR)
pca.frequency = SERVO_FREQ
servo = pca.channels[SERVO_CH]

print("RC steering via PCA9685 (CH1) — Ctrl+C to stop")

try:
    with RcPwmReader({"steer": CH1_STEER_PIN}, failsafe_s=0.25) as rx:
        while True:
            steer = rx.read("steer")
            set_servo_norm(servo, steer.norm)
            time.sleep(0.02)  # ~50Hz updates

except KeyboardInterrupt:
    print("\nStopping (Ctrl+C)")

finally:
    # Center + release
    set_servo_norm(servo, 0.0)
    time.sleep(0.1)
    servo.duty_cycle = 0
    pca.deinit()
    print("Steering centered, PCA9685 deinit.")
