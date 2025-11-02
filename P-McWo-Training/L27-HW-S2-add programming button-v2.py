import adafruit_dht
import board
import sys
import signal
import RPi.GPIO as GPIO
from time import monotonic

tempPIN = board.D4
dht = None
_cleaned = False
buttonPIN = 21
programState = 0

GPIO.setmode(GPIO.BCM)
GPIO.setup(buttonPIN, GPIO.IN,pull_up_down=GPIO.PUD_UP)

def read_temp():
    global dht
    try:
        t_c = dht.temperature
        if t_c is not None:
            return t_c
        else:
            print("Sensor reading failed, retrying...", flush=True)
            return None
    except RuntimeError as e:
        # Komt vaak voor, gewoon opnieuw proberen
        print(f"Reading error: {e}", flush=True)
        return None

def toggle_state():
    """Switch between normal and program mode."""
    global programState
    if programState == 0:
        programState = 1
        print("\n→ Switched to PROGRAM MODE\n", flush=True)
    else:
        programState = 0
        print("\n→ Switched to TEMPERATURE MODE\n", flush=True)
    
def destroy(SIGINT=None, SIGTERM=None):
    global dht, _cleaned
    if _cleaned:
        return
    _cleaned = True
    try:
        if dht is not None:
            dht.exit()
    except Exception as e:
        print(f"Cleanup warning: {e}", flush=True)
    GPIO.cleanup()
    print('Program Stopped', flush=True)
    sys.exit(0)

if __name__ == '__main__':
    print('Program is starting..., Press Ctrl+C to stop')
    signal.signal(signal.SIGINT, destroy)
    signal.signal(signal.SIGTERM, destroy)
    dht = adafruit_dht.DHT11(tempPIN)
    try:
        while True:
            if programState == 0:
                start = monotonic()
                temp = read_temp()
                if temp is not None:
                    print(f"T: {temp:.1f}°C", flush=True)
                else:
                    print("No valid reading.", flush=True)
                # Wait for button press (FALLING edge) or timeout
                # Return value: None if timeout, or channel number if pressed
                edge = GPIO.wait_for_edge(buttonPIN, GPIO.FALLING, timeout=int(10 * 1000))
                if edge is not None:
                    toggle_state()

            else:
                print("Program mode active. Press button to return.")
                # Wait indefinitely for button press (no timeout)
                GPIO.wait_for_edge(buttonPIN, GPIO.FALLING)
                toggle_state()
    except Exception as e:
        print(f"Program stopped by: {e}", flush=True)
        destroy()    

