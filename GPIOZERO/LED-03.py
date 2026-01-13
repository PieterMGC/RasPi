from gpiozero import LED
from signal import pause

led = LED(17)

try:
    led.on()
    pause()              # wait here until Ctrl+C
finally:
    led.close()

