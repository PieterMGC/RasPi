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
    roi = im[0:int(displ_h/2), 0:int(displ_w/2)]
    cv2.imshow("Camera", im)
    cv2.imshow("ROI", roi)
    if cv2.waitKey(1) == ord('q'):
        break
picam.stop()
picam.close()
cv2.destroyAllWindows()
print("All is closed")

