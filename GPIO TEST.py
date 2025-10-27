import RPi.GPIO as GPIO
from time import sleep

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.OUT)

def loop():
    while True:
        GPIO.output(17, True)

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