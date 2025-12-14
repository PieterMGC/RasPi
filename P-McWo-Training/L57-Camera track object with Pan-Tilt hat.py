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
cv2.createTrackbar('hue_low','My trackbars',25,179,TrackHL)
cv2.createTrackbar('hue_high','My trackbars',40,179,TrackHH)
cv2.createTrackbar('sat_low','My trackbars',100,255,TrackSL)
cv2.createTrackbar('sat_high','My trackbars',255,255,TrackSH)
cv2.createTrackbar('value_low','My trackbars',100,255,TrackVL)
cv2.createTrackbar('value_high','My trackbars',255,255,TrackVH)
pan_angle = 90
tilt_angle = 90
goto(pan_angle, tilt_angle)

while True:
    frame = picam.capture_array()
    frame = cv2.flip(frame, 0)
    frame_HSV = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    lower_bound = np.array([hue_low,sat_low,val_low])
    upper_bound = np.array([hue_high,sat_high,val_high])
    my_mask = cv2.inRange(frame_HSV,lower_bound,upper_bound)
    contours, junk = cv2.findContours(my_mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    
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






