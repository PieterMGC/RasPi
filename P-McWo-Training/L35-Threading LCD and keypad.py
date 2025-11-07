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

def read_kp():
    global myString
    while True:
        myString=myPad.return_sequence()
        sleep(.1)
        
readThread = threading.Thread(target=read_kp,)
readThread.deamon=True
readThread.start()
try:
    while True:
        CMD=myString
        if CMD == 'A'+ pwd:
            LCD1602.write(0,0,'Armed   ')
        elif CMD == 'B' + pwd:
            LCD1602.write(0,0,'UnArmed ')
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