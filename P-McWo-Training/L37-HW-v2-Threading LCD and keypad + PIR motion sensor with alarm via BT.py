#add motion sensor to make an alarm
#while the program is running, also thread for user input
#add alarm via BT speaker

import RPi.GPIO as GPIO
import LCD1602
from keypad_class import KeypadReader
from time import sleep
import threading
import sys

myPad = KeypadReader()
LCD1602.init(0x27,1)
myString = ''
pwd = '1234'
motionPIN = 7
armed = 0

GPIO.setmode(GPIO.BOARD)
GPIO.setup(motionPIN, GPIO.IN)

stop_event = threading.Event()

def read_kp():
    global myString
    while not stop_event.is_set() and myString != '*'+pwd:
        myString=myPad.return_sequence()
        sleep(.1)

def detect_motion():
    global motion
    while not stop_event.is_set():
        motion = GPIO.input(motionPIN)
        sleep(.05)
    
def alarm():
    global armed, motion
    if armed == 1:
        if motion == 1:
            LCD1602.write(0,1,'ALARM!!  ')
        else:
            LCD1602.write(0,1,'         ')

def destroy():
    stop_event.set()
    motionThread.join(timeout=1.0)
    readThread.join(timeout=1.0)
    try:
        LCD1602.clear()
    except Exception:
        pass  # ignore I2C errors during shutdown
    GPIO.cleanup()
    print('Program Stopped')
    sys.exit()

motionThread = threading.Thread(target=detect_motion,)
motionThread.daemon=True
motionThread.start()

readThread = threading.Thread(target=read_kp,)
readThread.daemon=True
readThread.start()

try:
    while myString != '*'+pwd:
        CMD = myString
        if CMD == 'A'+ pwd:
            armed = 1
        elif CMD == 'B' + pwd:
            armed = 0
        elif CMD == 'C' +  pwd:
            LCD1602.write(0,0,'New PWD?')
            while myString == 'C' + pwd:
                alarm()
            pwd=myString
            LCD1602.clear()
            LCD1602.write(0,0,'New PWD= '+pwd)
            sleep(2)
            LCD1602.clear()
        if armed == 1:
            LCD1602.write(0,0,'Armed   ')
            alarm()
        else:
            LCD1602.write(0,0,'UnArmed ')
            LCD1602.write(0,1,'         ')
        sleep(.1)
    destroy()

except KeyboardInterrupt:
    destroy()


