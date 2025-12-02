#use trackbars to set HSV values (low & high)

import cv2
import numpy as np
print(cv2.__version__)
from picamera2 import Picamera2

displ_w = 640
displ_h = 360

def TrackHL(val):
    global hue_low
    hue_low = val
    
def TrackHH(val):
    global hue_high
    hue_high = val
    
def TrackSL(val):
    global sat_low
    sat_low = val
    
def TrackSH(val):
    global sat_high
    sat_high = val
    
def TrackVL(val):
    global val_low
    val_low = val
    
def TrackVH(val):
    global val_high
    val_high = val

picam = Picamera2()
picam.preview_configuration.main.size = (displ_w,displ_h)
picam.preview_configuration.main.format = "RGB888"
picam.preview_configuration.controls.FrameRate = 60
picam.preview_configuration.align()
picam.configure("preview")
picam.start()

cv2.namedWindow('My trackbars')
cv2.createTrackbar('hue_low','My trackbars',10,179,TrackHL)
cv2.createTrackbar('hue_high','My trackbars',30,179,TrackHH)
cv2.createTrackbar('sat_low','My trackbars',100,255,TrackSL)
cv2.createTrackbar('sat_high','My trackbars',255,255,TrackSH)
cv2.createTrackbar('value_low','My trackbars',100,255,TrackVL)
cv2.createTrackbar('value_high','My trackbars',255,255,TrackVH)

while True:
    frame = picam.capture_array()
    frame_HSV = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    lower_bound = np.array([hue_low,sat_low,val_low])
    upper_bound = np.array([hue_high,sat_high,val_high])
    my_mask = cv2.inRange(frame_HSV,lower_bound,upper_bound)
    my_mask_small = cv2.resize(my_mask,(int(displ_w/2),int(displ_h/2)))
    object_of_interest = cv2.bitwise_and(frame,frame,mask=my_mask)
    object_of_interest_small = cv2.resize(object_of_interest,(int(displ_w/2),int(displ_h/2)))
    cv2.imshow("Camera", frame)
    cv2.imshow("my_mask",my_mask_small)
    cv2.imshow("ooi",object_of_interest_small)
    if cv2.waitKey(1) == ord('q'):
        break
picam.stop()
picam.close()
cv2.destroyAllWindows()
print("All is closed")




