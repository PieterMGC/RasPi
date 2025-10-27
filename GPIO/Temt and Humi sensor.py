import time
import adafruit_dht
import board

# GPIO19 is D19 in the 'board' module
dht = adafruit_dht.DHT11(board.D19)  # change to D4, D17, etc. if you move the wire

print("Reading DHT11 on GPIO19 (press Ctrl+C to stop)")
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
        dht.exit()
        raise e
    time.sleep(2)