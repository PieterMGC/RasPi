#Turn LED on/off with button

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

GPIO.setup(40, GPIO.IN)
GPIO.setup(16,GPIO.OUT)

try:
    while True:
        readVal = GPIO.input(40)
        print(readVal)
        print("-")
        GPIO.output(16,int(readVal))
        print(GPIO.input(16))
        GPIO.sleep(.5)
        
except KeyboardInterrupt:
    GPIO.cleanup()
    print('Quit')