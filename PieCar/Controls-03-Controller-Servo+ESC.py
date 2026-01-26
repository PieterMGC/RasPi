import time
from gpiozero import Servo
from rc_pwm_esc import RcPwmReader

STEER_OUT_PIN = 21   # servo
ESC_OUT_PIN   = 18   # pas aan indien nodig

steer_servo = Servo(STEER_OUT_PIN, min_pulse_width=0.0005, max_pulse_width=0.0025)
esc         = Servo(ESC_OUT_PIN,   min_pulse_width=0.0010, max_pulse_width=0.0020)

def throttle_forward_only(x):
    return 0.0 if x is None or x <= 0 else x

print("RC control running — Ctrl+C to stop")

try:
    with RcPwmReader({"steer": 22, "throttle": 27}, failsafe_s=0.25) as rx:
        while True:
            steer = rx.read("steer")
            thr   = rx.read("throttle")

            # Sturen: alleen afhangen van CH1
            if steer.norm is None:
                steer_servo.value = 0.0
            else:
                steer_servo.value = steer.norm

            # Motor: alleen afhangen van CH2
            esc.value = throttle_forward_only(thr.norm)

            # (optioneel) debug 1x per seconde-ish
            # print(f"steer={steer.norm} thr={thr.norm}", flush=True)

            time.sleep(0.02)

except KeyboardInterrupt:
    print("\nStopping (Ctrl+C)")

finally:
    try:
        esc.value = 0.0
        steer_servo.value = None
    except Exception:
        pass
    print("Motor stopped, steering centered.")