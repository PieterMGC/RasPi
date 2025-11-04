import RPi.GPIO as GPIO
from time import sleep
import ADC0834

def setup():
    GPIO.setmode(GPIO.BCM)
    ADC0834.setup()

def loop():
    while True:
        lightVAL = ADC0834.getResult(0)
        print(f"Light value: {lightVAL}")
        sleep(1)

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