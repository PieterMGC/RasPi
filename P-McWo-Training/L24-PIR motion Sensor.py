#GPIO4

import RPi.GPIO as GPIO
from time import sleep

motionPin = 4

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(motionPin, GPIO.IN)
    

def loop():
    while True:
        motion = GPIO.input(motionPin)
        print(motion)
        sleep(.5)

def destroy():
    GPIO.cleanup()
    print('Program Stopped')

if __name__ == '__main__':     #Program start from here
    print ('Program is starting...')
    setup()    
    sleep(10)
    print("Program started")

    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()