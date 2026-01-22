from gpiozero import Motor, MCP3008
from time import sleep
from signal import pause
from gpiozero.pins.lgpio import LGPIOFactory

factory = LGPIOFactory()
motor = Motor(forward=27, backward=17, enable=18, pwm=True, pin_factory=factory)
pot = MCP3008(channel=0)

try:
    while True:
        speed = pot.value
        if speed < 0.2:
            motor.stop()
        else:
            motor.forward(speed)
        sleep(0.5)                # 20 Hz update rate               
except KeyboardInterrupt:
    motor.stop()
    sleep(0.5)
    print("Program stopped!")