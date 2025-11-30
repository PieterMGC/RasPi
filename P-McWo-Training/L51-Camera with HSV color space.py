import cv2
import numpy as np
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

hue_low = 20
hue_high = 30
sat_low = 100
sat_high = 255
val_low = 100
val_high = 255

lower_bound = np.array([hue_low,sat_low,val_low])
upper_bound = np.array([hue_high,sat_high,val_high])



while True:
    frame = picam.capture_array()
    frame_HSV = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    my_mask = cv2.inRange(frame_HSV,lower_bound,upper_bound)
    my_mask_small = cv2.resize(my_mask,(int(displ_w/2),int(displ_h/2)))
    object_of_interest = cv2.bitwise_and(frame,frame,mask=my_mask)
    object_of_interest_small = cv2.resize(object_of_interest,(int(displ_w/2),int(displ_h/2)))
    #print(frame_HSV[int(displ_h/2),int(displ_w/2)])
    cv2.imshow("Camera", frame)
    cv2.imshow("my_mask",my_mask_small)
    cv2.imshow("ooi",object_of_interest_small)
    if cv2.waitKey(1) == ord('q'):
        break
picam.stop()
picam.close()
cv2.destroyAllWindows()
print("All is closed")

