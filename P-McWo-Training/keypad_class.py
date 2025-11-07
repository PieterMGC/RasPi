# Keypad to input sequence and print when D is pressed
# R0=11, R1=13, R2=15, R3=29, C0=31, C1=33, C2=35, C3=37

import RPi.GPIO as GPIO
from time import sleep

class KeypadReader:
    def __init__(self, rows=[11, 13, 15, 29], cols=[31, 33, 35, 37], keypad=[[1, 2, 3, 'A'],[4, 5, 6, 'B'],[7, 8, 9, 'C'],['*', 0, '#', 'D']],retChar='D'):
        self.rows = rows
        self.cols = cols
        self.keypad = keypad
        self.retChar = retChar
        self.output = ""
        self.setup()

    def setup(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.rows, GPIO.OUT)
        GPIO.setup(self.cols, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def read_keypad(self):
        read = None
        for i in range(4):
            for y in range(4):
                GPIO.output(self.rows[i], GPIO.HIGH)
                if GPIO.input(self.cols[y]) == 1:
                    read = self.keypad[i][y]
                    while GPIO.input(self.cols[y]) == 1:
                        sleep(.1)
                GPIO.output(self.rows[i], GPIO.LOW)
        return read

    def print_sequence(self):
        while True:
            value = self.read_keypad()
            if value != None and value != self.retChar:
                self.output += str(value)
            elif value == 'D':
                msg = self.output
                self.output = ""
                print(msg)
    
    def return_sequence(self):
        while True:
            value = self.read_keypad()
            if value != None and value != self.retChar:
                self.output += str(value)
            elif value == 'D':
                msg = self.output
                self.output = ""
                print(msg)
                return msg

    def destroy(self):
        GPIO.cleanup()
        print('Program Stopped')