#GPIO19, sudo pip3 install Adafruit_DHT --break-system-packages

import RPi.GPIO as GPIO
import dht11
from time import sleep
GPIO.cleanup()
myDHT = 0


def setup():
    global myDHT
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(19, GPIO.IN)
    myDHT = dht11.DHT11(pin = 19)

def loop():
    while True:
        result = myDHT.read()
        print('Temp = : ', result.temperature)
        print('Humidity = : ', result.humidity)
        if result.is_valid():
            print('Temp = : ', result.temperature)
            print('Humidity = : ', result.humidity)
        sleep(.2)

def destroy():
    GPIO.cleanup()
    print('Program Stopped')

if __name__ == '__main__':     #Program start from here
    print ('Program is starting...')
    setup()
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()