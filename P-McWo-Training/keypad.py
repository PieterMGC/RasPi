#R0=11, R1=13, R2=15, R3=29, C0=31, C1=33, C2=35, C3=37

import RPi.GPIO as GPIO
from time import sleep

rows = [11,13,15,29]
cols = [31,33,35,37]

keypad = [[1,2,3,'A'],[4,5,6,'B'],[7,8,9,'C'],['*',0,'#','D']]

def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(rows,GPIO.OUT)
    GPIO.setup(cols,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

def loop():
    myRow = int(input('Read row: '))
    myCol = int(input('Read col: '))
    while True:
        GPIO.output(rows[myRow],GPIO.HIGH)
        butVAL = GPIO.input(cols[myCol])
        GPIO.output(rows[myRow],GPIO.LOW)
        if butVAL ==1:
            print(keypad[myRow][myCol])
        sleep(.2)
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