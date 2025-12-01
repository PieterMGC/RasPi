import cv2
print(cv2.__version__)
import time
from picamera2 import Picamera2

displ_w = 1280
displ_h = 720
rect_color = (0,0,255)
def TrackX(val):
    global x_pos
    x_pos = val
    
def TrackY(val):
    global y_pos
    y_pos = val

def TrackW(val):
    global box_w
    box_w = val

def TrackH(val):
    global box_h
    box_h = val

picam = Picamera2()
picam.preview_configuration.main.size = (displ_w,displ_h)
picam.preview_configuration.main.format = "RGB888"
picam.preview_configuration.controls.FrameRate = 60
picam.preview_configuration.align()
picam.configure("preview")
picam.start()

cv2.namedWindow('My trackbars')
cv2.createTrackbar('X-pos','My trackbars',10,int(displ_w-1),TrackX)
cv2.createTrackbar('Y-pos','My trackbars',10,int(displ_h-1),TrackY)
cv2.createTrackbar('Box Width','My trackbars',10,int(displ_w/2),TrackW)
cv2.createTrackbar('Box Heigth','My trackbars',10,int(displ_h/2),TrackH)

while True:
    frame = picam.capture_array()
    roi = frame[y_pos:y_pos+box_h,x_pos:x_pos+box_w]
    cv2.rectangle(frame,(x_pos,y_pos),(x_pos+box_w,y_pos+box_h),rect_color,3)
    cv2.imshow("Camera", frame)
    cv2.imshow("ROI", roi)
    if cv2.waitKey(1) == ord('q'):
        break
picam.stop()
picam.close()
cv2.destroyAllWindows()
print("All is closed")

