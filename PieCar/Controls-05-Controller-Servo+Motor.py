import time
from gpiozero import Servo, Motor
from rc_pwm import RcPwmReader

# --- Receiver input GPIOs (BCM) ---
CH1_STEER_PIN = 22
CH2_THR_PIN   = 23

# --- Outputs ---
SERVO_PIN = 21   

# Motor driver pins
MOTOR_FWD_PIN = 27
MOTOR_BWD_PIN = 17
MOTOR_EN_PIN  = 18   # enable/PWM pin

# --- Devices ---
steer_servo = Servo(
    SERVO_PIN,
    min_pulse_width=0.0005,
    max_pulse_width=0.0025
)

motor = Motor(
    forward=MOTOR_FWD_PIN,
    backward=MOTOR_BWD_PIN,
    enable=MOTOR_EN_PIN,
    pwm=True
)

# --- Motor instellingen ---
THR_DEADBAND = 0.06   # tegen jitter rond neutraal

def apply_motor(thr_norm):
    """
    thr_norm: -1..+1 of None
    """
    if thr_norm is None or abs(thr_norm) < THR_DEADBAND:
        motor.stop()
        return

    speed = min(abs(thr_norm), 1.0)
    if thr_norm > 0:
        motor.forward(speed)
    else:
        motor.backward(speed)

print("RC running (CH1 steer, CH2 motor) — Ctrl+C to stop")

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
    motor.stop()
    steer_servo.value = None
    print("Motor stopped, steering centered.")