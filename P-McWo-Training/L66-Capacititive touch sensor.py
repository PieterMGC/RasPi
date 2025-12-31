import RPi.GPIO as GPIO
from time import sleep

touch_pin = 21

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(touch_pin, GPIO.IN)

def loop():
    while True:
        cap_state = GPIO.input(touch_pin)
        print(cap_state)
        sleep(.5)

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