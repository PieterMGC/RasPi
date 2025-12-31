#create logic to remember previous state to nextsteer a RGB led from R -> G -> B by pressing the captouch
import RPi.GPIO as GPIO
from time import sleep

touch_pin = 21
count = 0
prev_cap_state = 0

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(touch_pin, GPIO.IN)

def loop():
    while True:
        cap_state = GPIO.input(touch_pin)
        state = RememberState(cap_state)
        print(f"Cap Touch: {cap_state}, Count: {state}")
        sleep(.5)

def RememberState(cap_read):
    global prev_cap_state, count
    if prev_cap_state == 0 and cap_read == 1:
        count += 1
        prev_cap_state = 1
    if prev_cap_state == 1 and cap_read == 0:
        prev_cap_state = 0
    return count
        

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