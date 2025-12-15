import cv2
import numpy as np
print(cv2.__version__)
from picamera2 import Picamera2
from adafruit_servokit import ServoKit
from time import sleep

displ_w = 640
displ_h = 360

kit = ServoKit(channels=16)

# Tune per your hardware
kit.servo[0].set_pulse_width_range(500, 2500)  # tilt
kit.servo[1].set_pulse_width_range(500, 2500)  # pan

TILT = 0
PAN = 1

# Safe movement limits
PAN_MIN, PAN_MAX = 40, 140
TILT_MIN, TILT_MAX = 60, 120

def nothing(_): 
    pass

def goto(pan_angle, tilt_angle, pause=0.1):
    kit.servo[PAN].angle = pan_angle
    kit.servo[TILT].angle = tilt_angle
    sleep(pause)

picam = Picamera2()
picam.preview_configuration.main.size = (displ_w,displ_h)
picam.preview_configuration.main.format = "RGB888"
picam.preview_configuration.controls.FrameRate = 60
picam.preview_configuration.align()
picam.configure("preview")
picam.start()

cv2.namedWindow('My trackbars')
cv2.createTrackbar('hue_low','My trackbars',20,179,nothing)
cv2.createTrackbar('hue_high','My trackbars',100,179,nothing)
cv2.createTrackbar('sat_low','My trackbars',100,255,nothing)
cv2.createTrackbar('sat_high','My trackbars',255,255,nothing)
cv2.createTrackbar('value_low','My trackbars',100,255,nothing)
cv2.createTrackbar('value_high','My trackbars',255,255,nothing)
pan_angle = 90
tilt_angle = 90
goto(pan_angle, tilt_angle)
kernel = np.ones((5, 5), np.uint8)

while True:
    frame = picam.capture_array()
    frame = cv2.flip(frame, 0)
    frame_blur = cv2.GaussianBlur(frame, (5, 5), 0)
    frame_HSV = cv2.cvtColor(frame_blur,cv2.COLOR_RGB2HSV)
    hue_low  = cv2.getTrackbarPos("hue_low",  "My trackbars")
    hue_high = cv2.getTrackbarPos("hue_high", "My trackbars")
    sat_low  = cv2.getTrackbarPos("sat_low",  "My trackbars")
    sat_high = cv2.getTrackbarPos("sat_high", "My trackbars")
    val_low  = cv2.getTrackbarPos("value_low",  "My trackbars")
    val_high = cv2.getTrackbarPos("value_high", "My trackbars")
    #print(hue_low, hue_high, sat_low, sat_high, val_low, val_high)
    lower = np.array([hue_low,  sat_low,  val_low], dtype=np.uint8)
    upper = np.array([hue_high, sat_high, val_high], dtype=np.uint8)
    mask = cv2.inRange(frame_HSV,lower,upper)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
    contours, junk = cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours) > 0:
        contours = sorted(contours, key=lambda x:cv2.contourArea(x), reverse=True)
        contour = contours[0]
        x,y,w,h=cv2.boundingRect(contour)
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),3)
        
        error_w = (x+w/2)-displ_w/2
        error_h = (y+h/2)-displ_h/2

        if error_w > 25 and pan_angle < PAN_MAX:
            pan_angle += 1
        if error_w < -25 and pan_angle > PAN_MIN:
            pan_angle -= 1
        
        if error_h > 25 and tilt_angle < TILT_MAX:
            tilt_angle += 1
        if error_h < -25 and tilt_angle > TILT_MIN:
            tilt_angle -= 1
        
        kit.servo[PAN].angle = pan_angle
        kit.servo[TILT].angle = tilt_angle
    
    cv2.imshow("Camera", frame)
    
    if cv2.waitKey(1) == ord('q'):
        break
    
picam.stop()
picam.close()
cv2.destroyAllWindows()
print("All is closed")






