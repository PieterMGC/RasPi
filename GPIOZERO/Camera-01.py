from gpiozero import Button
from picamera2 import Picamera2
from datetime import datetime
from signal import pause

button = Button(2)

camera = Picamera2()
camera.configure(camera.create_still_configuration())
camera.start()

def capture():
    filename = f"/home/pieter/Documents/{datetime.now():%Y-%m-%d-%H-%M-%S}.jpg"
    camera.capture_file(filename)
    print(f"Saved {filename}")

button.when_pressed = capture

pause()