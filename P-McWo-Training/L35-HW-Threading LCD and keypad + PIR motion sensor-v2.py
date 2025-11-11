#add motion sensor to make an alarm
#while the program is running, also thread for user input

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

def read_kp():
    global myString
    while myString != '*':
        myString=myPad.return_sequence()
        sleep(.5)

def detect_motion():
    global motion
    while True:
        motion = GPIO.input(motionPIN)
    
def alarm():
    global armed, motion
    if armed == 1:
        if motion == 1:
            LCD1602.write(0,1,'ALARM!!  ')
        else:
            LCD1602.write(0,1,'         ')

def destroy():
    GPIO.cleanup()
    LCD1602.clear()
    print('Program Stopped')
    sys.exit()

#readThread = threading.Thread(target=new_pw,)
#readThread.deamon=True
#readThread.start()

readThread = threading.Thread(target=detect_motion,)
readThread.deamon=True
readThread.start()

readThread = threading.Thread(target=read_kp,)
readThread.deamon=True
readThread.start()

try:
    while myString != '*':
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
    destroy()

except KeyboardInterrupt:
    destroy()

