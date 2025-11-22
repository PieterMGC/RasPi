#create a bouncing box in the frame
import cv2
print(cv2.__version__)
import time
from picamera2 import Picamera2

res_w = 1280
res_h = 720

picam = Picamera2()
picam.preview_configuration.main.size = (res_w,res_h)
picam.preview_configuration.main.format = "RGB888"
picam.preview_configuration.controls.FrameRate = 30
picam.preview_configuration.align()
picam.configure("preview")
picam.start()

rect_up_left = (0,0)
rect_low_right = (50, 50)

while True:
    im = picam.capture_array()
    cv2.rectangle(im, rect_up_left, rect_low_right, (255, 0, 0), 5)
    cv2.imshow("Camera", im)
    if cv2.waitKey(1) == ord('q'):
        break
picam.stop()
picam.close()
cv2.destroyAllWindows()
print("All is closed")