#LED switches and stays ON or OFF on button press

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

GPIO.setup(40, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(16,GPIO.OUT)

try:
    while True:
        readVal = int(GPIO.input(40))
        LEDstate = int(GPIO.input(16))
        if readVal == 1:
                LEDstate = not LEDstate
                GPIO.output(16,LEDstate)
        
except KeyboardInterrupt:
    GPIO.cleanup()
    print('Quit')