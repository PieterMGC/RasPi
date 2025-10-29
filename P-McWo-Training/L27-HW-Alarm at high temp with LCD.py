#Use Buzzer, Temp sensor, potentiometer, button and LCD
#Give alarm outside temp range (or trip point). Temp range is set by potiometer.
#2 modes, set by button, monitor mode and program mode (for temp range), both shown on LCD

import adafruit_dht
import board
import sys
import signal
import time
import atexit
from datetime import datetime, timezone
import RPi.GPIO as GPIO

tempPIN = board.D4
buttonPIN = board.D21
READ_INTERVAL_S = 10
BACKOFF_MAX_S = 60
dht = None
_consecutive_errors = 0
_cleanup_ran = False  # prevent double cleanup if multiple signals fire

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
    dht = adafruit_dht.DHT11(tempPIN)
    print("Reading DHT11 (press Ctrl+C to stop)")
    backoff = 0
    while True:
        try:
            # Read values; these properties may raise RuntimeError on bad timing
            t_c = dht.temperature
            # Occasionally libs return None; treat as transient error
            if t_c is None:
                raise RuntimeError("Sensor returned None")
            # Success: reset error counters
            _consecutive_errors = 0
            backoff = 0
            print(f"T: {t_c:.1f}°C")
            time.sleep(READ_INTERVAL_S)
        except KeyboardInterrupt:
            # Redundant with SIGINT handler, but nice if signals are blocked
            print("\nKeyboard interrupt — exiting.")
            cleanup_and_quit(0)
        except RuntimeError as e:
            # Normal, expected transient errors from DHT sensors (timing/noise)
            _consecutive_errors += 1
            backoff = min((backoff * 2) if backoff else 2, BACKOFF_MAX_S)
            print(f"[retry #{_consecutive_errors}] {e}. Backing off {backoff}s…")
            time.sleep(backoff)

            if _consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                print("Too many consecutive errors. Is the sensor wired correctly?")
                cleanup_and_quit(1)
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