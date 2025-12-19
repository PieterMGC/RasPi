#calculate frames per seconds
import cv2
print(cv2.__version__)
import time
from picamera2 import Picamera2

fps = 30

picam = Picamera2()
picam.preview_configuration.main.size = (640,480)
picam.preview_configuration.main.format = "RGB888"
picam.preview_configuration.controls.FrameRate = fps
picam.preview_configuration.align()
picam.configure("preview")
picam.start()

pos = (30,60)
font = cv2.FONT_HERSHEY_SIMPLEX
height = 1.5
myColor = (0,0,255)
weight = 3
try:
    while True:
        count = 0
        start = time.time()
        while time.time() - start < 1:
            im = picam.capture_array()
            cv2.putText(im,'FPS: ' + str(fps),pos,font,height,myColor,weight)
            count += 1
            cv2.imshow("Camera", im)
        print (count)
        fps = count
        if (cv2.waitKey(1) & 0xFF) == ord('q'):
            break
finally:
    picam.stop()
    picam.close()
    cv2.destroyAllWindows()
    print("All is closed")

