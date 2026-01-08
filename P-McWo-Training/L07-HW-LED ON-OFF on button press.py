#LED switches and stays ON or OFF on button press

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

GPIO.setup(40, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(16,GPIO.OUT)

try:
    while True:
        readVal = int(GPIO.input(40))
        if readVal == 1 and GPIO.input(16) == 1:
                GPIO.output(16,0)
        elif readVal == 1 and GPIO.input(16) == 0:
                GPIO.output(16,1)
        
except KeyboardInterrupt:
    GPIO.cleanup()
    print('Quit')