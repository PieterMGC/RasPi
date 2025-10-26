#GPIO 7 (BCM 4), 5V!!

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

PWMpin = 4
GPIO.setup(PWMpin, GPIO.OUT)

PWM = GPIO.PWM(PWMpin, 50)
PWM.start(0)

try:
    while True:
        PWMPercent = float(input('PWM %?'))
        PWM.ChangeDutyCycle(PWMPercent)
        GPIO.sleep(.1)
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
    print("QUIT")