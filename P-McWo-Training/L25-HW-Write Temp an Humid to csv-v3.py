# DHT11 on BCM GPIO4 (board.D4)
import sys
import signal
import time
import atexit
import csv
from datetime import datetime, timezone
from pathlib import Path

import adafruit_dht
import board


# ---------- Settings ----------
PIN = board.D4                 # change to board.D19, ... if you move the wire
READ_INTERVAL_S = 10           # DHT11: don't read faster than ~1Hz; 10s is gentle
CSV_PATH = Path("temp_and_humid.csv")
TIMEZONE = timezone.utc        # or: datetime.now().astimezone().tzinfo for local
MAX_CONSECUTIVE_ERRORS = 10    # give up if sensor is disconnected/miswired
BACKOFF_MAX_S = 60             # cap retry backoff between failed reads
# ------------------------------

dht = None
_consecutive_errors = 0
_cleanup_ran = False  # prevent double cleanup if multiple signals fire


def ensure_csv_header(path: Path) -> None:
    """Create CSV with a header if it doesn't exist or is empty."""
    if not path.exists() or path.stat().st_size == 0:
        with path.open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["timestamp", "temperature_c", "humidity_pct"])


def write_csv_row(path: Path, ts: datetime, t_c: float, h_pct: float) -> None:
    """Append one reading to CSV. Use newline='' to avoid blank lines on Windows."""
    with path.open("a", newline="") as f:
        w = csv.writer(f)
        # ISO 8601 with timezone, to the second
        w.writerow([ts.isoformat(timespec="seconds"), f"{t_c:.1f}", f"{h_pct:.1f}"])


def cleanup_and_quit(exit_code: int = 0) -> None:
    """Release the GPIO line and exit once."""
    global _cleanup_ran, dht
    if _cleanup_ran:
        # Already cleaned; avoid exceptions during interpreter shutdown
        sys.exit(exit_code)
    _cleanup_ran = True
    try:
        if dht is not None:
            # Adafruit driver keeps resources; exit() releases them cleanly.
            dht.exit()
    except Exception as e:
        # Don't let cleanup issues block exit
        print(f"[cleanup] Ignored error during cleanup: {e}")
    finally:
        print("\nClean exit. GPIO released.")
        sys.exit(exit_code)


def _signal_handler(signum, frame):
    # Map signals to a friendly message and clean exit
    names = {signal.SIGINT: "SIGINT (Ctrl+C)", signal.SIGTERM: "SIGTERM"}
    print(f"\nReceived {names.get(signum, signum)} — shutting down…")
    cleanup_and_quit(0)


def main():
    global dht, _consecutive_errors

    # Prepare CSV file
    ensure_csv_header(CSV_PATH)

    # Create sensor on selected pin
    dht = adafruit_dht.DHT11(PIN)
    print("Reading DHT11 (press Ctrl+C to stop)")

    backoff = 0  # dynamic backoff seconds after transient errors

    while True:
        try:
            # Read values; these properties may raise RuntimeError on bad timing
            t_c = dht.temperature
            h = dht.humidity

            # Occasionally libs return None; treat as transient error
            if t_c is None or h is None:
                raise RuntimeError("Sensor returned None")

            # Success: reset error counters/backoff
            _consecutive_errors = 0
            backoff = 0

            now = datetime.now(TIMEZONE)
            print(f"{now.isoformat(timespec='seconds')} | T: {t_c:.1f}°C | H: {h:.1f}%")
            write_csv_row(CSV_PATH, now, t_c, h)

            # Gentle interval between reads
            time.sleep(READ_INTERVAL_S)

        except RuntimeError as e:
            # Normal, expected transient errors from DHT sensors (timing/noise)
            _consecutive_errors += 1
            backoff = min((backoff * 2) if backoff else 2, BACKOFF_MAX_S)
            print(f"[retry #{_consecutive_errors}] {e}. Backing off {backoff}s…")
            time.sleep(backoff)

            if _consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                print("Too many consecutive errors. Is the sensor wired correctly?")
                cleanup_and_quit(1)

        except KeyboardInterrupt:
            # Redundant with SIGINT handler, but nice if signals are blocked
            print("\nKeyboard interrupt — exiting.")
            cleanup_and_quit(0)

        except Exception as e:
            # Any unexpected error -> still release the pin before exiting
            print(f"Fatal error: {e!r}")
            cleanup_and_quit(1)


# Run cleanup at interpreter shutdown if we got here without signals/excepts
atexit.register(lambda: cleanup_and_quit(0))

# Register signal handlers *before* starting the main loop
signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)

if __name__ == "__main__":
    main()