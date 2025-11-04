#Alarm when room is dark and motion is detected
#Use photoresistor, buzzer(print) and PIR motion detector (GPIO4)

import RPi.GPIO as GPIO
from time import sleep
import ADC0834
from datetime import datetime

motionPIN = 4

def setup():
    GPIO.setmode(GPIO.BCM)
    ADC0834.setup()
    GPIO.setup(motionPIN, GPIO.IN)

def loop():
    while True:
        lightVAL = ADC0834.getResult(0)
        motion = GPIO.input(motionPIN)
        timeStamp = datetime.now()
        if motion == 1 and lightVAL <= 140:
            print("ALAAAAAAARM!!!!")
            print(timeStamp)
            print(f"Light value: {lightVAL}")
            print(f"Motion: {motion}")
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
