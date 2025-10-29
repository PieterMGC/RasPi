import adafruit_dht
import board
import sys
import signal
from time import sleep

#Temp
tempPIN = board.D4
dht = None

def setup():
    pass

def read_temp():
    t_c = dht.temperature
    if t_c is not None:
        print(f"T: {t_c:.1f}°C")
        return t_c
    else:
        print("Sensor reading failed, retrying...", flush=True)
         
            

def destroy(signum=None, frame=None):
    global dht
    if dht is not None:
        dht.exit()
    print('Program Stopped')
    sys.exit()


if __name__ == '__main__':     #Program start from here
    print ('Program is starting..., Press Crtl+C to stop')
    dht = adafruit_dht.DHT11(tempPIN)
    signal.signal(signal.SIGINT, destroy)   # Ctrl+C
    signal.signal(signal.SIGTERM, destroy)  # Service stop
    try:
        while True:
            temp = read_temp()
            print('temp = ', temp)
            sleep(10)
    except RuntimeError as e:
        # Komt vaak voor, sensor is even niet leesbaar
        print(f"Reading error: {e}", flush=True)
    except Exception as e:
        # Andere fouten → afsluiten
        print(f"Fatal error: {e}", flush=True)
        destroy()
