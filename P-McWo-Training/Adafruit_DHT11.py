#DTH11 = GPIO4

import sys, signal
import adafruit_dht, board
from time import sleep


dht = None

def cleanup_and_quit(signum=None, frame=None):
    global dht
    try:
        if dht is not None:
            dht.exit()          # <-- releases the GPIO line
    finally:
        print("\nClean exit. GPIO released.")
        sys.exit(0)
        

# Catch Ctrl+C and service stop
signal.signal(signal.SIGINT, cleanup_and_quit)
signal.signal(signal.SIGTERM, cleanup_and_quit)

try:
    dht = adafruit_dht.DHT11(board.D4)   # or board.D19 if you’re using GPIO19
    print("Reading DHT4 (press Ctrl+C to stop)")
    while True:
        try:
            t = dht.temperature
            h = dht.humidity
            if t is not None and h is not None:
                print(f"T: {t:.1f}°C | H: {h:.1f}%")                
            else:
                print("No data yet…")
        except RuntimeError as e:
            # normal transient errors from DHTs
            print(f"Retrying: {e}")
        sleep(1)
except Exception as e:
    # Any unexpected error -> still release the pin
    print(f"Fatal error: {e}")
    cleanup_and_quit()
finally:
    # Also release on normal interpreter shutdown
    cleanup_and_quit()

