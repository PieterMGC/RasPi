import lgpio
import time

PIN = 22  # BCM22

h = lgpio.gpiochip_open(0)

# Claim als "alert" zodat edge events gegarandeerd binnenkomen
lgpio.gpio_claim_alert(h, PIN, lgpio.BOTH_EDGES)

rise = None

def cb(chip, gpio, level, tick):
    global rise
    if level == 1:
        rise = tick
    elif level == 0 and rise is not None:
        width_us = (tick - rise) / 1000.0
        print(f"{width_us:.0f} us", flush=True)
        rise = None

# BELANGRIJK: bewaar het callback-object in een variabele
c = lgpio.callback(h, PIN, lgpio.BOTH_EDGES, cb)

print("Luisteren op GPIO22... beweeg stuur.", flush=True)
while True:
    time.sleep(1)