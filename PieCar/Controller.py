import lgpio
import time

PIN = 22  # BCM4

h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_input(h, PIN, lgpio.SET_PULL_DOWN)

def cb(chip, gpio, level, tick):
    print("EDGE", level)

lgpio.callback(h, PIN, lgpio.BOTH_EDGES, cb)

print("Beweeg stuur/trigger...")
while True:
    time.sleep(1)