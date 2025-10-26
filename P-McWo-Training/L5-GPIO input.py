import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

GPIO.setup(40, GPIO.IN)

try:
    while True:
        readVal = GPIO.input(40)
        print(readVal)
        GPIO.sleep(.5)
        
except KeyboardInterrupt:
    GPIO.cleanup()
    print('Quit')