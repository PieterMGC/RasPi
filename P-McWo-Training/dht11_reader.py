# dht11_reader.py

import sys
import signal
import adafruit_dht
import board
from time import sleep


class DHT11Reader:
    """
    Simple wrapper around adafruit_dht.DHT11 that:
    - encapsulates init / cleanup
    - provides a read() method returning (temperature, humidity)
    """

    def __init__(self, pin=board.D4, auto_init=True):
        self.pin = pin
        self._sensor = None
        if auto_init:
            self.init_sensor()

    def init_sensor(self):
        """Create the underlying DHT11 object if not already created."""
        if self._sensor is None:
            self._sensor = adafruit_dht.DHT11(self.pin)

    def read(self):
        """
        Read temperature (°C) and humidity (%).

        Returns:
            (temperature, humidity) as floats, or (None, None) if no data.

        Raises:
            RuntimeError for the usual transient DHT read errors so caller
            can decide how to handle / retry.
        """
        if self._sensor is None:
            self.init_sensor()

        try:
            t = self._sensor.temperature
            h = self._sensor.humidity
            if t is None or h is None:
                return None, None
            return t, h
        except RuntimeError:
            # normal transient errors from DHT sensors
            raise

    def close(self):
        """Release the GPIO pin / sensor."""
        if self._sensor is not None:
            try:
                # Your original code used .exit() to release GPIO
                self._sensor.exit()
            except AttributeError:
                # In case the library version changes and has no exit()
                pass
            finally:
                self._sensor = None


def main(pin=board.D4):
    """
    Example usage: continuous reading with clean exit on Ctrl+C.
    Run this file directly to use it.
    """
    reader = DHT11Reader(pin=pin)

    def _cleanup_and_quit(signum=None, frame=None):
        reader.close()
        print("\nClean exit. GPIO released.")
        sys.exit(0)

    # Catch Ctrl+C and service stop (same idea as your original script)
    signal.signal(signal.SIGINT, _cleanup_and_quit)
    signal.signal(signal.SIGTERM, _cleanup_and_quit)

    print(f"Reading DHT11 on pin {pin} (press Ctrl+C to stop)")

    try:
        while True:
            try:
                t, h = reader.read()
                if t is not None and h is not None:
                    print(f"T: {t:.1f}°C | H: {h:.1f}%")
                else:
                    print("No data yet…")
            except RuntimeError as e:
                print(f"Retrying: {e}")
            sleep(1)
    finally:
        # Also release on “normal” termination
        reader.close()
        print("Reader closed, GPIO released.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)