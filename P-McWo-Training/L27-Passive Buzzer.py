import RPi.GPIO as GPIO
import time

buzzPin = 17
buzzPWM = 0

def setup():
    global buzzPWM
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(buzzPin, GPIO.OUT)
    buzzPWM = GPIO.PWM(buzzPin, 200)
    buzzPWM.start(10)

def loop():
    global buzzPWM
    while True:
        for i in range(200,1500):
            buzzPWM.ChangeFrequency(i)
            time.sleep(.001)
        for i in range(1500,200,-1):
            buzzPWM.ChangeFrequency(i)
            time.sleep(.001)

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

