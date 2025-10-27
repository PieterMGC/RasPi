#Turn on LED when motion is detected
#PIR = GPIO4, LED = GPIO17

import RPi.GPIO as GPIO
from time import sleep, time
from datetime import datetime

motionPin = 4
LED = 17
timeStamp = 0
timeOn = 0
count = 0

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(motionPin, GPIO.IN)
    GPIO.setup(LED, GPIO.OUT)    

def write_to_file():
    global timeStamp, timeOn, count
    with open("detection.txt", "a") as f:
        f.write(timeStamp.isoformat('#', 'seconds') + "\n")
        f.write("Time = " + str(timeOn) + "\n")
        f.write("Count = " + str(count) + "\n\n")
        
def loop():
    global timeStamp, timeOn, count
    prevMotion = 0
    while True:
        motion = GPIO.input(motionPin)
        GPIO.output(LED, motion)
        if motion == 1:
            timeStart = time()
            timeStamp = datetime.now()
            prevMotion = 1
            count += 1
        while motion == 1:
            motion = GPIO.input(motionPin)
        timeStop = time()
        if prevMotion == 1:
            timeOn = round(timeStop - timeStart, 2)
            write_to_file()
            prevMotion = 0
        #sleep(.5)

def destroy():
    GPIO.cleanup()
    print('Program Stopped')

if __name__ == '__main__':     #Program start from here
    print ('Program is starting...')
    setup()    
    sleep(10)
    print("Program started")

    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()