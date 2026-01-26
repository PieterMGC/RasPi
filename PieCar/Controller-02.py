import lgpio
import time

PIN = 22  # BCM22

CENTER_US = 1500
SPAN_US   = 500      # 1000..2000 => +/-500 rond 1500
DEAD_US   = 30       # deadzone rond center

h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_alert(h, PIN, lgpio.BOTH_EDGES)

rise_tick = None
last_pulse_time = 0
last_us = None

def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x

def norm_from_us(us):
    # deadzone
    d = us - CENTER_US
    if abs(d) < DEAD_US:
        d = 0
    x = d / SPAN_US
    return clamp(x, -1.0, 1.0)

def cb(chip, gpio, level, tick):
    global rise_tick, last_pulse_time, last_us
    if level == 1:
        rise_tick = tick
    elif level == 0 and rise_tick is not None:
        width_us = (tick - rise_tick) / 1000.0
        rise_tick = None

        last_us = width_us
        last_pulse_time = time.monotonic()

# callback handle bewaren!
c = lgpio.callback(h, PIN, lgpio.BOTH_EDGES, cb)

print("PWM lezen op GPIO22 (CH1). Beweeg stuur.", flush=True)

while True:
    now = time.monotonic()

    # failsafe: geen pulse > 0.2s => None/stop
    if now - last_pulse_time > 0.2:
        print("NO SIGNAL", flush=True)
    elif last_us is not None:
        x = norm_from_us(last_us)
        print(f"{last_us:7.1f} us   steer={x:+.2f}", flush=True)

    time.sleep(0.1)