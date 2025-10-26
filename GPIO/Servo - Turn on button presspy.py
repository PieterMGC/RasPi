import RPi.GPIO as GPIO
import time

OFFSE_DUTY = 0        #define pulse offset of servo
SERVO_MIN_DUTY = 2.5+OFFSE_DUTY     #define pulse duty cycle for minimum angle of servo
SERVO_MAX_DUTY = 12.5+OFFSE_DUTY    #define pulse duty cycle for maximum angle of servo
servoPin = 7
B_left = 40
B_right = 36
turn = 0
angle = 90
radius = 5
speed = .05

def map( value, fromLow, fromHigh, toLow, toHigh):
    return (toHigh-toLow)*(value-fromLow) / (fromHigh-fromLow) + toLow

def setup():
    global p
    GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
    GPIO.setup(servoPin, GPIO.OUT)   # Set servoPin's mode is output
    GPIO.output(servoPin, GPIO.LOW)  # Set servoPin to low
    GPIO.setup([B_left, B_right], GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set GPIO buttons as input
    p = GPIO.PWM(servoPin, 50)     # set Frequece to 50Hz
    p.start(0)                     # Duty Cycle = 0
    
def servoWrite():      # make the servo rotate to specific angle (0-180 degrees) 
    global angle
    if(angle<0):
        angle = 0
    elif(angle > 180):
        angle = 180
    p.ChangeDutyCycle(map(angle,0,180,SERVO_MIN_DUTY,SERVO_MAX_DUTY)) #map the angle to duty cycle and output it

def buttonRead(): #read the state of the button and set the turn direction
    global turn
    B_press_left = int(GPIO.input(B_left))
    B_press_right = int(GPIO.input(B_right))
    if B_press_left == 1:
        turn = 'L'
    if B_press_right == 1:
        turn = 'R'

def angleWrite(): #translate the turn direction to an angle
    global angle, turn
    if turn == 'L':
        angle -= radius
    if turn == 'R':
        angle += radius
    turn = 0


def loop():
    while True:
        buttonRead()
        #print('turn= ', turn)
        time.sleep(speed)
        angleWrite()
        #print('angle= ', angle)
        servoWrite()

def destroy():
    angle = 90
    p.ChangeDutyCycle(map(angle,0,180,SERVO_MIN_DUTY,SERVO_MAX_DUTY))
    time.sleep(.5)
    p.stop()
    GPIO.cleanup()

if __name__ == '__main__':     #Program start from here
    print ('Program is starting...')
    setup()
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()