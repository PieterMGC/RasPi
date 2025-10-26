import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

GPIO.setup([11,12,13,15,16],GPIO.OUT)
myPWM_11 = GPIO.PWM(11,100)

myPWM_11.start(100)
GPIO.sleep(5)
myPWM_11.ChangeDutyCycle(10)

#myPWM_11.ChangeFrequency(5)
try:
    while True:
        pass

        
except KeyboardInterrupt:
    GPIO.cleanup()
    print('Quit')
