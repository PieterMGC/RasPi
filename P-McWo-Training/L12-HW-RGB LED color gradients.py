#Turn RGB LED corresponding colors on with buttons
#make LED colors dimmable with buttons, 0 -> 100 -> 0


import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

L_red = 37
L_green = 35
L_blue = 33
B_red = 40
B_green = 38
B_blue = 36
Step = 1.5
R_Bright = .9
G_Bright = .9
B_Bright = .9

GPIO.setup([L_red, L_green, L_blue], GPIO.OUT)
GPIO.setup([B_red, B_green, B_blue], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

RED_PWM = GPIO.PWM(L_red, 100)
RED_PWM.start(int(R_Bright))
GREEN_PWM = GPIO.PWM(L_green, 100)
GREEN_PWM.start(int(G_Bright))
BLUE_PWM = GPIO.PWM(L_blue, 100)
BLUE_PWM.start(int(B_Bright))

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
        GPIO.sleep(.5)
        read_buttons()
        #read_LEDstate()
        if I_red == 1 and R_Bright < 100 and R_Bright*Step < 100:
            R_Bright *= Step
            RED_PWM.ChangeDutyCycle(R_Bright)
        if (I_red == 1 and R_Bright) >= 100 or (I_red == 1 and R_Bright*Step >= 100):
            R_Bright = 0.9
            RED_PWM.ChangeDutyCycle(int(R_Bright))
            
        if I_green == 1 and G_Bright < 100 and G_Bright*Step < 100:
            G_Bright *= Step
            GREEN_PWM.ChangeDutyCycle(G_Bright)
        if (I_green == 1 and G_Bright) >= 100 or (I_green == 1 and G_Bright*Step >= 100):
            G_Bright = 0.9
            GREEN_PWM.ChangeDutyCycle(int(G_Bright))
            
        if I_blue == 1 and B_Bright < 100 and B_Bright*Step < 100:
            B_Bright *= Step
            BLUE_PWM.ChangeDutyCycle(B_Bright)
        if (I_blue == 1 and B_Bright) >= 100 or (I_blue == 1 and B_Bright*Step >= 100):
            B_Bright = 0.9
            BLUE_PWM.ChangeDutyCycle(int(B_Bright))
            
        print(int(R_Bright), int(G_Bright), int(B_Bright))

except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
    print("Quit")