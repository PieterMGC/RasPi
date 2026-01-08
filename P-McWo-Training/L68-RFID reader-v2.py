import time
import RPi.GPIO as GPIO
from mfrc522 import MFRC522

POLL_DELAY = 0.1
REPEAT_SUPPRESS_S = 1.5   # ignore same UID for this many seconds

GPIO.setmode(GPIO.BCM)

r = MFRC522()
r.Init()
r.AntennaOn()

last_uid_hex = None
last_seen_ts = 0.0

def uid_to_hex(uid_list):
    return ":".join(f"{b:02X}" for b in uid_list)

try:
    print("Scanning... present/remove tag anytime (Ctrl+C to stop)")
    while True:
        (status, tag_type) = r.Request(r.PICC_REQIDL)

        if status == r.MI_OK:
            (status, uid) = r.Anticoll()

            if status == r.MI_OK:
                uid_hex = uid_to_hex(uid)
                now = time.time()

                is_repeat = (uid_hex == last_uid_hex) and ((now - last_seen_ts) < REPEAT_SUPPRESS_S)

                if not is_repeat:
                    print("Tag detected!",
                          "type:", hex(tag_type),
                          "UID:", uid_hex)

                last_uid_hex = uid_hex
                last_seen_ts = now

        time.sleep(POLL_DELAY)

except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()