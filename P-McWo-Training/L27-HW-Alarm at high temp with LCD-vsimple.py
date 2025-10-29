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

def loop():
    while True:
        t_c = dht.temperature
        if t_c is not None:
            print(f"T: {t_c:.1f}°C")
        sleep(10)          
            

def destroy():
    global dth
    if dht is not None:
        dth.exit()
    print('Program Stopped')


if __name__ == '__main__':     #Program start from here
    print ('Program is starting...')
    dht = adafruit_dht.DHT11(tempPIN)
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()
    finally:
        print('Everything Cleaned')
        sys.exit()
