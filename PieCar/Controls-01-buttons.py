#GPIO19 = Right
#GPIO26 = Left
#GPIO20 = Backward
#GPIO21 = Forward

from gpiozero import Button, Motor, Servo
from time import sleep
from signal import pause
from gpiozero.pins.lgpio import LGPIOFactory

factory = LGPIOFactory()

but_r = Button(19, pin_factory=factory)
but_l = Button(26, pin_factory=factory)
but_fwd = Button(21, pin_factory=factory)
but_bwd = Button(20, pin_factory=factory)

motor = Motor(forward=27, backward=17, enable=18, pwm=True, pin_factory=factory)
servo = Servo(4, min_pulse_width = 0.5/1000, max_pulse_width = 2.5/1000,pin_factory=factory)

def drive():
    # --- Drive callbacks ---
    def on_fwd_pressed():
        if not but_bwd.is_pressed:   # only drive forward if not also holding backward
            motor.forward()

    def on_bwd_pressed():
        if not but_fwd.is_pressed:   # only drive backward if not also holding forward
            motor.backward()

    def on_drive_released():
        # stop if neither direction button is still pressed
        if not but_fwd.is_pressed and not but_bwd.is_pressed:
            motor.stop()

    but_fwd.when_pressed = on_fwd_pressed
    but_bwd.when_pressed = on_bwd_pressed
    but_fwd.when_released = on_drive_released
    but_bwd.when_released = on_drive_released

def steer():
    # --- Steering callbacks ---
    def on_right_pressed():
        if not but_l.is_pressed:
            servo.max()

    def on_left_pressed():
        if not but_r.is_pressed:
            servo.min()

    def on_steer_released():
        # center if neither steering button is still pressed
        if not but_l.is_pressed and not but_r.is_pressed:
            servo.mid()

    but_r.when_pressed = on_right_pressed
    but_l.when_pressed = on_left_pressed
    but_r.when_released = on_steer_released
    but_l.when_released = on_steer_released

def main():
    print("Program started! Stop by pressing Ctrl+C")
    drive()
    steer()
    pause()  # sleep forever; event callbacks do the work

try:
    main()
except KeyboardInterrupt:
    motor.stop()
    sleep(0.5)
    servo.value = None  # release servo signal
    sleep(0.5)
    print("Program stopped!")
