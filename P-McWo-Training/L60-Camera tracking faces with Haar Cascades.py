import cv2
print(cv2.__version__)
print("Optimized:", cv2.useOptimized())
from picamera2 import Picamera2

displ_w = 640
displ_h = 360
DETECT_SCALE = 0.5

picam = Picamera2()
picam.preview_configuration.main.size = (displ_w,displ_h)
picam.preview_configuration.main.format = "RGB888"
picam.preview_configuration.controls.FrameRate = 60
picam.preview_configuration.align()
picam.configure("preview")
picam.start()

eye_cascade = cv2.CascadeClassifier('./haar/haarcascade_eye.xml')
face_cascade = cv2.CascadeClassifier('./haar/haarcascade_frontalface_default.xml')

if face_cascade.empty():
    raise FileNotFoundError(f"Face cascade not loaded: {FACE_XML}")
if eye_cascade.empty():
    raise FileNotFoundError(f"Eye cascade not loaded: {EYE_XML}")

cv2.setUseOptimized(True)

try:
    while True:
        frame = picam.capture_array()
        frame = cv2.flip(frame, -1)
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_small = cv2.resize(frame_gray, None, fx=DETECT_SCALE, fy=DETECT_SCALE, interpolation=cv2.INTER_LINEAR)
        frame_small = cv2.equalizeHist(frame_small)
        faces = face_cascade.detectMultiScale(frame_small,scaleFactor=1.3,minNeighbors=5,minSize=(30, 30))
        # Terugschalen naar originele coördinaten
        inv = 1.0 / DETECT_SCALE
        for (sx, sy, sw, sh) in faces:
            x = int(sx * inv)
            y = int(sy * inv)
            w = int(sw * inv)
            h = int(sh * inv)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            # --- Eye detectie binnen face ROI (ook geschaald) ---
            face_roi_gray = frame_gray[y:y+h, x:x+w]
            if face_roi_gray.size == 0:
                continue
            face_small = cv2.resize(face_roi_gray, None, fx=DETECT_SCALE, fy=DETECT_SCALE, interpolation=cv2.INTER_LINEAR)
            eyes = eye_cascade.detectMultiScale(face_small, scaleFactor=1.15, minNeighbors=5, minSize=(12, 12))
            inv_face = 1.0 / DETECT_SCALE
            for (ex, ey, ew, eh) in eyes:
                ex2 = x + int(ex * inv_face)
                ey2 = y + int(ey * inv_face)
                ew2 = int(ew * inv_face)
                eh2 = int(eh * inv_face)
                cv2.rectangle(frame, (ex2, ey2), (ex2 + ew2, ey2 + eh2), (0, 255, 0), 2)
        cv2.imshow("Camera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    picam.stop()
    picam.close()
    cv2.destroyAllWindows()
    print("All is closed")
