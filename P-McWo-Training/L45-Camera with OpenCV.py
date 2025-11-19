import cv2
print(cv2.__version__)
from time import sleep
from picamera2 import Picamera2

picam2 = Picamera2()
picam2.preview.configuration.main.size = (1280,720)
picam2.preview.configuration.main.format = "RGB888"
picam2.preview.configuration.align()
picam2.configue("preview")
picam2.start()

while True:
    im = picam2.capture_array()
    cv2.imshow("Camera", im)
    if cv2.waitkey(1) == ord('q'):
        break
cam.release()
cv2.destroyAllWindows()
