import RPi.GPIO as GPIO
#print(help(GPIO))

#Set GPIO mode to Board
GPIO.setmode(GPIO.BOARD)

#Setup GPIO pin
GPIO.setup(11,GPIO.OUT)

#Get user input
Timer = int(input("How long should the LED be on:"))

#Switch LED
GPIO.output(11,True)
print(GPIO.input(11))
GPIO.sleep(Timer)
GPIO.output(11,False)
print(GPIO.input(11))
GPIO.cleanup()




