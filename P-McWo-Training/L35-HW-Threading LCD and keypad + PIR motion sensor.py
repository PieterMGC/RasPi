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
    while True:
        myString=myPad.return_sequence()
        sleep(.1)

def detect_motion():
    global motion
    while True:
        motion = GPIO.input(motionPIN)
    

def new_pw():
    global myString, pwd
    temp_PWD = myString
    while True:
        if temp_PWD == 'C' + pwd:
            LCD1602.write(0,0,'New PWD?')
            while myString == 'C' + pwd:
                pass
            pwd = myString
            LCD1602.clear()
            LCD1602.write(0,0,'New PWD= '+pwd)
            sleep(2)
            LCD1602.clear()

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
    while True:
        CMD = myString
        if CMD == 'A'+ pwd:
            LCD1602.write(0,0,'Armed   ')
            armed = 1
            if motion == 1:
                LCD1602.write(0,1,'ALARM!!  ')
            else:
                LCD1602.write(0,1,'         ')
        elif CMD == 'B' + pwd:
            LCD1602.write(0,0,'UnArmed ')
            LCD1602.write(0,1,'         ')
            armed = 0
        elif CMD == 'C' +  pwd:
            LCD1602.write(0,0,'New PWD?')
            while myString == 'C' + pwd:
                pass
            pwd=myString
            LCD1602.clear()
            LCD1602.write(0,0,'New PWD= '+pwd)
            sleep(2)
            LCD1602.clear()
except KeyboardInterrupt:
    GPIO.cleanup()
    LCD1602.clear()
    print('Program Stopped')
    sys.exit()
