import time
import adafruit_dht
import board

# GPIO19 is D19 in the 'board' module


dht = adafruit_dht.DHT11(board.D4)  # change to D4, D17, etc. if you move the wire

print("Reading DHT11 on GPIO4 (press Ctrl+C to stop)")

def cleanup_and_quit(signum=None, frame=None):
    global dht
    try:
        if dht is not None:
            dht.exit()          # <-- releases the GPIO line
    finally:
        print("\nClean exit. GPIO released.")
        sys.exit(0)
        
while True:
    try:
        temp_c = dht.temperature
        hum = dht.humidity
        if temp_c is not None and hum is not None:
            print(f"Temperature: {temp_c:.1f}°C  |  Humidity: {hum:.1f}%")
        else:
            print("No data yet...")
    except RuntimeError as e:
        # DHTs are chatty and often throw transient errors; just retry
        print(f"Retrying: {e}")
    except Exception as e:
        cleanup_and_quit()
        raise e
    time.sleep(2)