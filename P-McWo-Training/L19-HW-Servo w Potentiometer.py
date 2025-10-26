#Move the servo smooth with potentiometer

import RPi.GPIO as GPIO
import ADC0834
from time import sleep

OFFSE_DUTY = 0        #define pulse offset of servo
SERVO_MIN_DUTY = 2.5+OFFSE_DUTY     #define pulse duty cycle for minimum angle of servo
SERVO_MAX_DUTY = 12.5+OFFSE_DUTY    #define pulse duty cycle for maximum angle of servo
servoPin = 23

def setup():
    global servo
    GPIO.setmode(GPIO.BCM)       # Numbers GPIOs by physical location
    GPIO.setup(servoPin, GPIO.OUT)   # Set servoPin's mode is output
    GPIO.output(servoPin, GPIO.LOW)  # Set servoPin to low
    servo = GPIO.PWM(servoPin, 50)     # set Frequece to 50Hz
    servo.start(0)
    ADC0834.setup()# Duty Cycle = 0

def map( value, fromLow, fromHigh, toLow, toHigh):
    return (toHigh-toLow)*(value-fromLow) / (fromHigh-fromLow) + toLow

def readPot():
    global analogVal
    analogVal = ADC0834.getResult(0)

def pot_to_angle():
    global analogVal, angle
    angle = map(analogVal,255,0,SERVO_MIN_DUTY,SERVO_MAX_DUTY)

def loop():
    while True:
        readPot()
        pot_to_angle()
        servo.ChangeDutyCycle(angle)

def destroy():
    angle = 90
    servo.ChangeDutyCycle(map(angle,0,180,SERVO_MIN_DUTY,SERVO_MAX_DUTY))
    sleep(1)
    servo.stop()
    GPIO.cleanup()
    print('Program Stopped')

if __name__ == '__main__':     #Program start from here
    print ('Program is starting...')
    setup()
    try:
        loop()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
        destroy()