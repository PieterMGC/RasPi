from gpiozero import AngularServo, MCP3008
from time import sleep

servo = AngularServo(4, min_angle=0, max_angle=100)
pot = MCP3008(channel=0)

try:
    while True:
        servo.angle = int(pot.value * 100)
except KeyboardInterrupt:
    servo.value = None  # release servo signal
    sleep(0.5)
    print("Program stopped!")


    