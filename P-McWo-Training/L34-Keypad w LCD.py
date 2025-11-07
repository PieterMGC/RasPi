import RPi.GPIO as GPIO
from time import sleep
from keypad_class import KeypadReader
import LCD1602

myKeypad = KeypadReader()
LCD1602.init(0x27,1)

def setup():
    GPIO.setmode(GPIO.BOARD)

def loop():
    while True:
        myString = ''
        LCD1602.write(0,0,'Input Value: ')
        myString=myKeypad.return_sequence()
        if myString != None:
            LCD1602.clear()
            LCD1602.write(0,0,'Input was: ')
            LCD1602.write(0,1,str(myString))
        sleep(5)
        LCD1602.clear()

def destroy():
    GPIO.cleanup()
    LCD1602.clear()
    print('Program Stopped')

if __name__ == '__main__':     #Program start from here
    print ('Program is starting...')
    setup()
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()