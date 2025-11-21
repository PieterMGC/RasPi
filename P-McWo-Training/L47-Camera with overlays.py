#overlays
import cv2
print(cv2.__version__)
import time
from picamera2 import Picamera2

fps = 30

picam = Picamera2()
picam.preview_configuration.main.size = (1280,720)
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

upper_left = (250,50)
lower_right = (350, 125)
r_color = (255,0,0)
r_thick = 10

cent = (640,360)
c_color = (0,255,0)
r = 35
c_thick = 5

while True:
    count = 0
    start = time.time()
    while time.time() - start < 1:
        im = picam.capture_array()
        cv2.putText(im,'FPS: ' + str(fps),pos,font,height,myColor,weight)
        count += 1
        cv2.rectangle(im, upper_left, lower_right, r_color, r_thick)
        cv2.circle(im,cent,r,c_color,c_thick)
        cv2.imshow("Camera", im)
    print (count)
    print(im[0,0])
    fps = count
    if cv2.waitKey(1) == ord('q'):
        break
picam.stop()
picam.close()
cv2.destroyAllWindows()
print("All is closed")


