import time
import smbus
from gpiozero import Servo
from gpiozero.pins.lgpio import LGPIOFactory
from rc_pwm import RcPwmReader

# --- Receiver input GPIOs (BCM) ---
CH1_STEER_PIN = 22
CH2_THR_PIN   = 23

# --- Outputs ---
SERVO_PIN = 21

# --- Grove I2C Motor Driver ---
I2C_BUS = 1
MOTOR_ADDR = 0x0F   # jouw adres

MOTOR_SPEED_REG = 0x82
MOTOR_DIR_REG   = 0xAA

# --- Devices ---
# Option 3: force lgpio pin factory (no PWMSoftwareFallback)
factory = LGPIOFactory()  

steer_servo = Servo(
    SERVO_PIN,
    min_pulse_width=0.0010, max_pulse_width=0.0020, #limit servo angle
    pin_factory=factory
)

bus = smbus.SMBus(I2C_BUS)

# --- Motor instellingen ---
THR_DEADBAND = 0.06   # tegen jitter rond neutraal

def motor_stop():
    bus.write_i2c_block_data(MOTOR_ADDR, MOTOR_SPEED_REG, [0, 0])

def apply_motor(thr_norm):
    """
    thr_norm: -1..+1 of None
    M1 only, M2 always 0
    """
    if thr_norm is None or abs(thr_norm) < THR_DEADBAND:
        motor_stop()
        return

    speed_255 = int(min(abs(thr_norm), 1.0) * 255)

    if thr_norm > 0:
        bus.write_i2c_block_data(MOTOR_ADDR, MOTOR_DIR_REG, [1, 0])  # M1 fwd, M2 off
    else:
        bus.write_i2c_block_data(MOTOR_ADDR, MOTOR_DIR_REG, [2, 0])  # M1 rev, M2 off

    bus.write_i2c_block_data(MOTOR_ADDR, MOTOR_SPEED_REG, [speed_255, 0])

print("RC running (CH1 steer, CH2 motor via Grove I2C) — Ctrl+C to stop")

try:
    with RcPwmReader(
        {"steer": CH1_STEER_PIN, "throttle": CH2_THR_PIN},
        failsafe_s=0.25
    ) as rx:

        while True:
            steer = rx.read("steer")
            thr   = rx.read("throttle")

            # --- Servo ---
            steer_servo.value = 0.0 if steer.norm is None else steer.norm

            # --- Motor ---
            apply_motor(thr.norm)

            time.sleep(0.02)   # ~50 Hz

except KeyboardInterrupt:
    print("\nStopping (Ctrl+C)")

finally:
    motor_stop()
    steer_servo.value = None
    print("Motor stopped, steering centered.")
