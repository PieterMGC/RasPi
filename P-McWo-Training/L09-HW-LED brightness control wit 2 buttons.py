#control brightness of LED with 2 buttons, in-/decrement with 10 by eacht press
#extra credit for turning LED ON/OFF

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

LED = 11
Min = 38
Plus = 40
Step = 10
Bright = 50

GPIO.setup(LED,GPIO.OUT)
GPIO.setup([Min, Plus], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

LED_PWM = GPIO.PWM(LED, 100)
LED_PWM.start(Bright)

try:
    while True:
       GPIO.sleep(.1)
       print(Bright)
       readDec = int(GPIO.input(Min))
       readInc = int(GPIO.input(Plus))
       print(readInc, readDec)
       if readInc == 0 and readDec == 0:
           counter = 0
           print(counter)
       while counter == 0:
           readDec = int(GPIO.input(Min))
           readInc = int(GPIO.input(Plus))
           if readInc == 1 and Bright < 100:
               Bright += Step
               LED_PWM.ChangeDutyCycle(Bright)
               counter += 1
           elif  readDec == 1 and Bright > 0:
               Bright -= Step
               LED_PWM.ChangeDutyCycle(Bright)
               counter += 1
      
except KeyboardInterrupt:
    pass
finally:
    LED_PWM.stop()
    GPIO.cleanup()
    print("Quit")
