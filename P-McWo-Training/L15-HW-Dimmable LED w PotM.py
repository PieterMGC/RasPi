#Make a dimmable RED LED

import RPi.GPIO as GPIO
import ADC0834
from time import sleep

GPIO.setmode(GPIO.BCM)
ADC0834.setup()

Bright = 0
LED = 21
GPIO.setup(LED,GPIO.OUT)
LED_PWM = GPIO.PWM(LED, 100)
LED_PWM.start(Bright)

def map_255_to_100(value):
    return (value/255)*100

def readPot():
    global analogVal
    analogVal = ADC0834.getResult(0)

try:
    while True:
        readPot()
        Bright = map_255_to_100(analogVal)
        LED_PWM.ChangeDutyCycle(Bright)
except KeyboardInterrupt:
    pass
finally:
    LED_PWM.stop()
    GPIO.cleanup()
    print("QUIT")