import RPi.GPIO as GPIO
import dht11
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)          # IMPORTANT
#GPIO.cleanup()                  # start clean

sensor = dht11.DHT11(pin=4)    # BCM 19 (physical pin 35)

try:
    while True:
        result = sensor.read()
        if result.is_valid():
            print(f"OK  -> {result.temperature:.1f}°C | {result.humidity:.1f}%")
        else:
            # show error code to diagnose (0..5 depending on lib)
            print(f"Fail -> error_code={getattr(result,'error_code', 'n/a')}")
        time.sleep(2)           # DHT11 needs ~1s min between reads
finally:
    GPIO.cleanup()