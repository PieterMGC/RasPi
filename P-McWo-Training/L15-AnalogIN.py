#import RPi.GPIO as GPIO
import ADC0834
from time import sleep

#GPIO.setmode(GPIO.BCM)
ADC0834.setup()

try:
    while True:
        analogVal = ADC0834.getResult(0)
        print(analogVal)
        sleep(.5)
except KeyboardInterrupt:
    pass
finally:
    #GPIO.cleanup()
    print("QUIT")