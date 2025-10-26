import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

RED = 37
GREEN = 35
BLUE = 33

GPIO.setup([RED, GREEN, BLUE], GPIO.OUT)
try:   
    while True:
        GPIO.output(BLUE, 1)
        GPIO.output(RED, 1)
        GPIO.output(GREEN, 1)

except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
    print("Quit")