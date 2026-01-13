from gpiozero import DistanceSensor, Motor
from signal import pause

sensor = DistanceSensor(23, 24, max_distance=1, threshold_distance=0.2)
motor = Motor(forward=27, backward=17, enable=18)

sensor.when_in_range = motor.forward
sensor.when_out_of_range = motor.stop

pause()