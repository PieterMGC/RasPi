import cv2
print(cv2.__version__)
import time
from picamera2 import Picamera2

displ_w = 640
displ_h = 360

picam = Picamera2()
picam.preview_configuration.main.size = (displ_w,displ_h)
picam.preview_configuration.main.format = "RGB888"
picam.preview_configuration.controls.FrameRate = 60
picam.preview_configuration.align()
picam.configure("preview")
picam.start()

eyes_cascade = cv2.CascadeClassifier('./haar/haarcascade_eye.xml')
face_cascade = cv2.CascadeClassifier('./haar/haarcascade_frontalface_default.xml')

while True:
    frame = picam.capture_array()
    frame = cv2.flip(frame, -1)
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(frame_gray,1.3,5)
    for face in faces:
       x,y,w,h = face
       cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),3)
       roi = frame[y:y+h,x:x+w]
       roi_gray = frame_gray[y:y+h,x:x+w]
       eyes = eyes_cascade.detectMultiScale(roi_gray)
       for eye in eyes:
          x,y,w,h = eye
          cv2.rectangle(roi_color,(x,y),(x+w,y+h),(0,255,0),3)
    cv2.imshow("Camera", frame)
    if cv2.waitKey(1) == ord('q'):
        break
picam.stop()
picam.close()
cv2.destroyAllWindows()
print("All is closed")