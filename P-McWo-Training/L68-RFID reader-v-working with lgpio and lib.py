# scan_uid.py
import time
from rc522_lgpio import RC522Reader

POLL_DELAY = 0.05
IGNORE_REPEAT_S = 1.5

def main():
    last_uid = None
    last_uid_ts = 0.0

    with RC522Reader(
        spi_bus=0,
        spi_dev=0,        # CE0
        spi_speed=200_000,
        rst_gpio=25,      # BCM 25
        gpiochip=0,
        reset_idle_s=1.0, # self-heal interval
        wakeup=True,      # use WUPA (more reliable)
    ) as reader:
        print("Scanning... present/remove tag anytime. Ctrl+C to stop.")
        try:
            while True:
                ev = reader.poll()
                if ev:
                    now = time.time()
                    is_repeat = (ev.uid_hex == last_uid) and ((now - last_uid_ts) < IGNORE_REPEAT_S)
                    if not is_repeat:
                        print(f"UID={ev.uid_hex}  type=0x{ev.tag_type:02X}")
                        last_uid = ev.uid_hex
                        last_uid_ts = now

                time.sleep(POLL_DELAY)
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()
