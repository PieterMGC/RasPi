import lgpio
import time

# GPIO mapping (BCM)
STEER_PIN    = 22   # CH1
THROTTLE_PIN = 23   # CH2

CENTER_US = 1500
SPAN_US   = 500
DEAD_US   = 30
FAILSAFE_S = 0.2

h = lgpio.gpiochip_open(0)

lgpio.gpio_claim_alert(h, STEER_PIN,    lgpio.BOTH_EDGES)
lgpio.gpio_claim_alert(h, THROTTLE_PIN, lgpio.BOTH_EDGES)

state = {
    STEER_PIN:    {"rise": None, "last_us": None, "last_t": 0},
    THROTTLE_PIN: {"rise": None, "last_us": None, "last_t": 0},
}

def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x

def norm_from_us(us):
    d = us - CENTER_US
    if abs(d) < DEAD_US:
        d = 0
    return clamp(d / SPAN_US, -1.0, 1.0)

def cb(chip, gpio, level, tick):
    s = state[gpio]
    if level == 1:
        s["rise"] = tick
    elif level == 0 and s["rise"] is not None:
        s["last_us"] = (tick - s["rise"]) / 1000.0
        s["last_t"] = time.monotonic()
        s["rise"] = None

# callback handles bewaren
c1 = lgpio.callback(h, STEER_PIN,    lgpio.BOTH_EDGES, cb)
c2 = lgpio.callback(h, THROTTLE_PIN, lgpio.BOTH_EDGES, cb)

print("CH1=steer, CH2=throttle", flush=True)

while True:
    now = time.monotonic()

    def read(pin):
        s = state[pin]
        if now - s["last_t"] > FAILSAFE_S or s["last_us"] is None:
            return None, None
        return s["last_us"], norm_from_us(s["last_us"])

    steer_us, steer = read(STEER_PIN)
    thr_us, thr     = read(THROTTLE_PIN)

    if steer is None or thr is None:
        print("FAILSAFE", flush=True)
    else:
        print(
            f"steer={steer:+.2f} ({steer_us:7.1f} us) | "
            f"throttle={thr:+.2f} ({thr_us:7.1f} us)",
            flush=True
        )

    time.sleep(0.5)