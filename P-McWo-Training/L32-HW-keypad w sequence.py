#Keypad to input sequence and print when D is pressed
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

def read_keypad():
    read = None
    for i in range(4):
        for y in range(4):
            GPIO.output(rows[i],GPIO.HIGH)
            if GPIO.input(cols[y]) == 1:
                read = keypad[i][y]             
                while GPIO.input(cols[y]) == 1:
                    sleep(.1)
            GPIO.output(rows[i],GPIO.LOW)
    return read

def print_sequence():
    output = ""
    while True:
       value = read_keypad()
       if value != None and value != 'D':
           output = output + str(value)
       elif value == 'D':
           print(output)
           output = ""

def destroy():
    GPIO.cleanup()
    print('Program Stopped')

if __name__ == '__main__':     #Program start from here
    print ('Program is starting...')
    setup()
    try:
        print_sequence()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()