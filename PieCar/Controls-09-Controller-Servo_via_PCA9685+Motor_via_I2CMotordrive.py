import time
import smbus

import board
import busio
from adafruit_pca9685 import PCA9685

from rc_pwm import RcPwmReader


# --- Receiver input GPIOs (BCM) ---
CH1_STEER_PIN = 22
CH2_THR_PIN   = 23

# --- Grove I2C Motor Driver (your working address) ---
I2C_BUS = 1
MOTOR_ADDR = 0x0F
MOTOR_SPEED_REG = 0x82
MOTOR_DIR_REG   = 0xAA

# --- Motor settings ---
THR_DEADBAND = 0.06   # jitter around neutral
last_dir = 0  # 0 brake, 1 fwd, 2 rev

# =========================
# PCA9685 Servo settings
# =========================
PCA9685_ADDR = 0x40          # default address for most boards
SERVO_CH = 0                 # channel you plugged the servo into
SERVO_FREQ = 50              # 50 Hz for RC servos

# Limit to ~180°: use a safe 1000..2000 us range (common for 180° travel)
SERVO_MIN_US = 1000
SERVO_MAX_US = 2000

# Optional: center trim (in microseconds). Use 0 unless your center is off.
SERVO_TRIM_US = 0


def us_to_duty(us: float) -> int:
    """
    Convert pulse width in microseconds to PCA9685 16-bit duty_cycle value.
    At 50Hz, period = 20,000 us.
    """
    us = max(SERVO_MIN_US, min(SERVO_MAX_US, us))
    period_us = 1_000_000.0 / SERVO_FREQ  # 20_000 us at 50Hz
    return int((us / period_us) * 65535)


def set_servo_norm(channel, norm: float | None):
    """
    norm: -1..+1 (None = center)
    maps to SERVO_MIN_US..SERVO_MAX_US
    """
    if norm is None:
        norm = 0.0

    norm = max(-1.0, min(1.0, float(norm)))

    mid = (SERVO_MIN_US + SERVO_MAX_US) / 2.0 + SERVO_TRIM_US
    span = (SERVO_MAX_US - SERVO_MIN_US) / 2.0
    us = mid + (norm * span)

    channel.duty_cycle = us_to_duty(us)


# =========================
# Grove Motor (M1 only)
# =========================
bus = smbus.SMBus(I2C_BUS)

def motor_stop():
    # M1 = 0, M2 = 0
    bus.write_i2c_block_data(MOTOR_ADDR, MOTOR_SPEED_REG, [0, 0])

def apply_motor(thr_norm):
    global last_dir

    if thr_norm is None or abs(thr_norm) < THR_DEADBAND:
        bus.write_i2c_block_data(MOTOR_ADDR, MOTOR_SPEED_REG, [0, 0])
        last_dir = 0
        return

    speed = int(min(abs(thr_norm), 1.0) * 255)
    new_dir = 1 if thr_norm > 0 else 2

    # Only change DIR when needed
    if new_dir != last_dir:
        bus.write_i2c_block_data(MOTOR_ADDR, MOTOR_DIR_REG, [new_dir, 0])
        last_dir = new_dir
        time.sleep(0.002)  # tiny settle delay helps some boards

    # Always update speed
    bus.write_i2c_block_data(MOTOR_ADDR, MOTOR_SPEED_REG, [speed, 0])


# =========================
# Main
# =========================
print("Init PCA9685...")
i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c, address=PCA9685_ADDR)
pca.frequency = SERVO_FREQ
servo = pca.channels[SERVO_CH]

print("RC running (CH1 steer via PCA9685, CH2 motor via Grove I2C) — Ctrl+C to stop")

try:
    with RcPwmReader(
        {"steer": CH1_STEER_PIN, "throttle": CH2_THR_PIN},
        failsafe_s=0.25
    ) as rx:

        while True:
            steer = rx.read("steer")
            thr   = rx.read("throttle")
            
            #debug throttle
            #thr_us = thr.us
            #thr_norm = thr.norm
            #print(f"thr_us={thr_us if thr_us is not None else 'None'}  thr_norm={thr_norm if thr_norm is not None else 'None'}")
            # --- Servo via PCA9685 ---
            set_servo_norm(servo, steer.norm)

            # --- Motor via Grove (M1 only) ---
            apply_motor(thr.norm)

            time.sleep(0.02)  # ~50 Hz

except KeyboardInterrupt:
    print("\nStopping (Ctrl+C)")

finally:
    motor_stop()
    # Center steering on exit
    set_servo_norm(servo, 0.0)
    time.sleep(0.1)
    pca.deinit()
    print("Motor stopped, steering centered, PCA9685 deinit.")
