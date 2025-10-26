#Turn RGB LED corresponding colors on with buttons

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

L_red = 37
L_green = 35
L_blue = 33
B_red = 40
B_green = 38
B_blue = 36

GPIO.setup([L_red, L_green, L_blue], GPIO.OUT)
GPIO.setup([B_red, B_green, B_blue], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def read_buttons():
    global I_red, I_green, I_blue
    I_red = int(GPIO.input(B_red))
    I_green = int(GPIO.input(B_green))
    I_blue = int(GPIO.input(B_blue))
    
def read_LEDstate():
    global LS_red, LS_green, LS_blue
    LS_red = int(GPIO.input(L_red))
    LS_green = int(GPIO.input(L_green))
    LS_blue = int(GPIO.input(L_blue))
    
try:   
    while True:
        GPIO.sleep(.1)
        read_buttons()
        read_LEDstate()
        if I_red == 1:
            LS_red = not LS_red
            GPIO.output(L_red,LS_red)
        if I_green == 1:
            LS_green = not LS_green
            GPIO.output(L_green,LS_green)
        if I_blue == 1:
            LS_blue = not LS_blue
            GPIO.output(L_blue,LS_blue)    

except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
    print("Quit")