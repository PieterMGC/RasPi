#with buffering, writing data to SD every 5 min

import sys
import signal
import time
import csv
from datetime import datetime, timezone
from pathlib import Path
import adafruit_dht
import board

# ---- Configuration ----
PIN = board.D4
CSV_PATH = Path("temp_and_humid.csv")
READ_INTERVAL_S = 10         # Sensor polling interval
WRITE_INTERVAL_S = 300       # How often to write buffer (e.g. 5 minutes)
TIMEZONE = timezone.utc
# ------------------------

dht = None
buffer = []                  # In-memory buffer for recent readings
last_write_time = 0


def ensure_csv_header():
    """Ensure CSV file has a header if new or empty."""
    if not CSV_PATH.exists() or CSV_PATH.stat().st_size == 0:
        with CSV_PATH.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "temperature_C", "humidity_%"])


def flush_buffer():
    """Write all buffered readings to disk."""
    global buffer, last_write_time
    if not buffer:
        return
    try:
        with CSV_PATH.open("a", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(buffer)
        print(f"📝 Wrote {len(buffer)} readings to disk.")
    except Exception as e:
        print(f"⚠️ Failed to write CSV: {e}")
    finally:
        buffer.clear()
        last_write_time = time.time()


def cleanup_and_quit(signum=None, frame=None):
    """Flush data, release GPIO, and exit safely."""
    print("\nStopping… flushing buffer and cleaning up.")
    flush_buffer()
    if dht is not None:
        try:
            dht.exit()
        except Exception:
            pass
    print("GPIO released. Exiting.")
    sys.exit(0)


# Catch Ctrl+C or service stop
signal.signal(signal.SIGINT, cleanup_and_quit)
signal.signal(signal.SIGTERM, cleanup_and_quit)

# Prepare CSV and sensor
ensure_csv_header()
dht = adafruit_dht.DHT11(PIN)
print("Logging DHT11 data every 10s, writing to SD every 5min. Press Ctrl+C to stop.")

try:
    while True:
        try:
            t = dht.temperature
            h = dht.humidity
            if t is not None and h is not None:
                now = datetime.now(TIMEZONE)
                buffer.append([now.isoformat(timespec="seconds"), f"{t:.1f}", f"{h:.1f}"])
                print(f"{now.isoformat(timespec='seconds')} | T: {t:.1f}°C | H: {h:.1f}%")
            else:
                print("No valid reading, retrying...")

            # Periodically flush buffer to disk
            if time.time() - last_write_time >= WRITE_INTERVAL_S:
                flush_buffer()

        except RuntimeError as e:
            # Typical transient error
            print(f"Retrying: {e}")

        time.sleep(READ_INTERVAL_S)

except KeyboardInterrupt:
    cleanup_and_quit()