from gpiozero import Button
from picamera2 import Picamera2, Preview
from datetime import datetime
from signal import pause

button = Button(2)

camera = Picamera2()

#camera.start()

def preview():
    camera.configure(camera.create_preview_configuration())
    camera.start_preview(Preview.QTGL)
    camera.start()

def stop():
    camera.stop()

def capture():
    filename = f"/home/pieter/Documents/{datetime.now():%Y-%m-%d-%H-%M-%S}.jpg"
    camera.capture_file(filename)
    print(f"Saved {filename}")

button.when_pressed = preview
button.when_released = stop

pause()