from gpiozero import Motor, MCP3008
from time import sleep
from signal import pause
from gpiozero.pins.lgpio import LGPIOFactory

factory = LGPIOFactory()
motor = Motor(forward=27, backward=17, enable=18, pwm=True, pin_factory=factory)
pot = MCP3008(channel=0)

try:
    while True:
        v = pot.value
        if v < 0.48 and v > 0.1:
            motor.backward((0.5 - v) * 2)
        elif v > 0.52:
            motor.forward((v - 0.5) * 2)
        else:
            motor.stop()
        sleep(0.5)                              
except KeyboardInterrupt:
    motor.stop()
    sleep(0.5)
    print("Program stopped!")
