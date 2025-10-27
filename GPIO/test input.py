import RPi.GPIO as GPIO, time
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN)  # no internal pull-up
for _ in range(20):
    print("GPIO4 level:", GPIO.input(4))
    time.sleep(0.1)
GPIO.cleanup()