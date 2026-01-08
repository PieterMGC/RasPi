import RPi.GPIO as GPIO
#print(help(GPIO))

#Set variables
Cont = 'Y'

#Set GPIO mode to Board
GPIO.setmode(GPIO.BOARD)

#Setup GPIO pin
GPIO.setup(11,GPIO.OUT)

#Stay running
while Cont == 'Y':
    #Get user input
    Amount = int(input("How many times should the LED blink:"))
    #Switch LED
    for i in range(Amount):
        GPIO.output(11,True)
        print(GPIO.input(11))
        GPIO.sleep(1)
        GPIO.output(11,False)
        GPIO.sleep(1)
        print(GPIO.input(11))
    Cont = input('Continue? (Y/N): ')

#clean GPIO
GPIO.cleanup()



