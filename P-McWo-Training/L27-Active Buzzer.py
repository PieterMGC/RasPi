import RPi.GPIO as GPIO
import time

buzzPin = 17


def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(buzzPin, GPIO.OUT)

def loop():
    while True:
        GPIO.output(buzzPin, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(buzzPin, GPIO.LOW)
        time.sleep(1)

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
