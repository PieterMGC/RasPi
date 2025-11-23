#create a bouncing box in the frame
#optimise by just changing direction step = step*-1
import cv2
print(cv2.__version__)
import time
from picamera2 import Picamera2
import random

res_w = 640
res_h = 380
box_w = 50
box_h = 50

picam = Picamera2()
picam.preview_configuration.main.size = (res_w,res_h)
picam.preview_configuration.main.format = "RGB888"
picam.preview_configuration.controls.FrameRate = 30
picam.preview_configuration.align()
picam.configure("preview")
picam.start()

x = random.randint(0, res_w-box_w)
y = random.randint(0, res_h-box_h)

rect_up_left = (x,y)
rect_low_right = (x+box_w, y+box_h)

horizontal = random.choice([1,-1])
vertical = random.choice([1,-1])

while True:
    im = picam.capture_array()
    if x + box_w == res_w - 1 or x == 0:
        horizontal = horizontal * (-1)
    if y + box_h == res_h - 1 or y == 0:
        vertical = vertical * (-1)
    x += horizontal
    y += vertical
    rect_up_left = (x, y)
    rect_low_right = (x + box_w, y + box_h)
    cv2.rectangle(im, rect_up_left, rect_low_right, (255, 0, 0), 5)
    cv2.imshow("Camera", im)
    if cv2.waitKey(1) == ord('q'):
        break
picam.stop()
picam.close()
cv2.destroyAllWindows()
print("All is closed")
