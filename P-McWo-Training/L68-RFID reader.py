#only works with badge presented at startup

from mfrc522 import SimpleMFRC522
import time
import RPi.GPIO as GPIO

reader = SimpleMFRC522()

try:
    while True:
        print("Waiting for 13.56MHz tag (Ctrl+C to stop)...")
        uid, text = reader.read()
        print("UID:", uid)
        print("Text:", repr(text))
        time.sleep(0.5)

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()