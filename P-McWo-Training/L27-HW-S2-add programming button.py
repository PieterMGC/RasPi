import adafruit_dht
import board
import sys
import signal
from time import sleep
import RPi.GPIO as GPIO

tempPIN = board.D4
dht = None
_cleaned = False
buttonPIN = board.D21

GPIO.setup(buttonPIN, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

def read_button():
    buttonVAL = GPIO.input(buttonPIN)
    return buttonVAL

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
    print('Program Stopped', flush=True)
    sys.exit(0)

if __name__ == '__main__':
    print('Program is starting..., Press Ctrl+C to stop')
    signal.signal(signal.SIGINT, destroy)
    signal.signal(signal.SIGTERM, destroy)
    dht = adafruit_dht.DHT11(tempPIN)
    try:
        while True:
            temp = read_temp()
            buttonVAL = read_button()
            print(buttonVAL)
            if temp is not None:
                print(f"T: {temp:.1f}°C", flush=True)
            sleep(10)
    except Exception as e:
        print(f"Program stopped by: {e}", flush=True)
        destroy()    
