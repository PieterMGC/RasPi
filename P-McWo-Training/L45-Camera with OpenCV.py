import cv2
print(cv2.__version__)
import time
from picamera2 import Picamera2

displ_w = 1280
displ_h = 720

picam = Picamera2()
picam.preview_configuration.main.size = (displ_w,displ_h)
picam.preview_configuration.main.format = "RGB888"
picam.preview_configuration.controls.FrameRate = 60
picam.preview_configuration.align()
picam.configure("preview")
picam.start()

while True:
    im = picam.capture_array()
    cv2.imshow("Camera", im)
    if cv2.waitKey(1) == ord('q'):
        break
picam.stop()
picam.close()
cv2.destroyAllWindows()
print("All is closed")
