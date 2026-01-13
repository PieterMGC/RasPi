from gpiozero import Robot, Motor, Button
from signal import pause

motor = Motor(forward=27, backward=17, enable=18, pwm=True)

fw = Button(21)
bw = Button(20)
while True:
    fw.when_pressed = motor.forward
    fw.when_released = motor.stop
    
    bw.when_pressed = motor.backward
    bw.when_released = motor.stop