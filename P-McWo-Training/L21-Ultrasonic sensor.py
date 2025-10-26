import RPi.GPIO as GPIO
from time import sleep, time

trigPin = 20
echoPin = 21
echoStartTime = 0
echoStopTime = 0

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(trigPin, GPIO.OUT)
    GPIO.setup(echoPin, GPIO.IN)

def trigger():
    GPIO.output(trigPin, 0)
    sleep(2E-6)
    GPIO.output(trigPin, 1)
    sleep(10E-6)
    GPIO.output(trigPin, 0)

def listen():
    global echoStartTime, echoStopTime
    while GPIO.input(echoPin) == 0:
        pass
    echoStartTime = time()
    while GPIO.input(echoPin) == 1:
        pass
    echoStopTime = time()
    
def loop():
    while True:
        trigger()
        listen()
        pingTravelTime = echoStopTime - echoStartTime
        print(pingTravelTime * 17150)
        sleep(.5)


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