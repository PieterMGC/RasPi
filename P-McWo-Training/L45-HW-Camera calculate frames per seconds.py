#calculate frames per seconds
import cv2
print(cv2.__version__)
import time
from picamera2 import Picamera2

picam = Picamera2()
picam.preview_configuration.main.size = (1280,720)
picam.preview_configuration.main.format = "RGB888"
picam.preview_configuration.controls.FrameRate = 30
picam.preview_configuration.align()
picam.configure("preview")
picam.start()

while True:
    count = 0
    start = time.time()
    while time.time() - start < 1:
        im = picam.capture_array()
        count += 1
        cv2.imshow("Camera", im)
    print (count)
    if cv2.waitKey(1) == ord('q'):
        break
picam.stop()
picam.close()
cv2.destroyAllWindows()
print("All is closed")

