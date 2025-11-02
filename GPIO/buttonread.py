import RPi.GPIO as GPIO
import time

BUTTON_BCM = 21

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_BCM, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def button_pressed(channel):
    print("Button pressed!")

# Detect rising edge on GPIO21
GPIO.add_event_detect(BUTTON_BCM, GPIO.RISING, callback=button_pressed, bouncetime=200)

print("Waiting for button press... Press Ctrl+C to exit.")
try:
    while True:
        time.sleep(1)  # just keep running
except KeyboardInterrupt:
    print("Exiting...")
finally:
    GPIO.cleanup()