#count up from 0 to 31 and light up the correct of 5 LEDs to represent the binary representation of the number
#upgrade the code to request a number and show it binary on the LED's

import RPi.GPIO as GPIO
#print(help(GPIO))

#Set GPIO mode to Board
GPIO.setmode(GPIO.BOARD)

#Setup GPIO pin
GPIO.setup([11,12,13,15,16],GPIO.OUT)

#Make LEDs blink sequentially
try:
    a = 0
    for a in range(32):
        bin_a = list(format(a, '05b'))
        print(bin_a)
        GPIO.output(11,int(bin_a[0]))
        GPIO.output(12,int(bin_a[1]))
        GPIO.output(13,int(bin_a[2]))
        GPIO.output(15,int(bin_a[3]))
        GPIO.output(16,int(bin_a[4]))
        GPIO.sleep(1)
        GPIO.output([11,12,13,15,16],0)
        GPIO.sleep(1)

#clean GPIO
except KeyboardInterrupt:
    print('Quit')
    GPIO.cleanup()    
    
