import cv2
import numpy as np
import time
from picamera2 import Picamera2
from adafruit_servokit import ServoKit

print("OpenCV:", cv2.__version__)

displ_w = 640
displ_h = 360

# --- Servos ---
kit = ServoKit(channels=16)

TILT = 0
PAN = 1

# Tune per your hardware
kit.servo[TILT].set_pulse_width_range(500, 2500)
kit.servo[PAN].set_pulse_width_range(500, 2500)

# Safe movement limits
PAN_MIN, PAN_MAX = 40, 140
TILT_MIN, TILT_MAX = 60, 120

def clamp(v, vmin, vmax):
    return max(vmin, min(vmax, v))

def goto(pan_angle, tilt_angle):
    kit.servo[PAN].angle = pan_angle
    kit.servo[TILT].angle = tilt_angle

# --- Trackbar callbacks (no-op; we'll read values directly) ---
def nothing(_): pass

# --- Camera ---
picam = Picamera2()
picam.preview_configuration.main.size = (displ_w, displ_h)
picam.preview_configuration.main.format = "RGB888"   # => frame is RGB
picam.preview_configuration.controls.FrameRate = 60
picam.preview_configuration.align()
picam.configure("preview")
picam.start()

# --- UI ---
cv2.namedWindow("My trackbars", cv2.WINDOW_NORMAL)

cv2.createTrackbar("hue_low",   "My trackbars", 20, 179, nothing)
cv2.createTrackbar("hue_high",  "My trackbars", 100, 179, nothing)
cv2.createTrackbar("sat_low",   "My trackbars", 100, 255, nothing)
cv2.createTrackbar("sat_high",  "My trackbars", 255, 255, nothing)
cv2.createTrackbar("val_low",   "My trackbars", 100, 255, nothing)
cv2.createTrackbar("val_high",  "My trackbars", 255, 255, nothing)

# --- Initial angles ---
pan_angle = 90
tilt_angle = 90
goto(pan_angle, tilt_angle)

# --- Tracking params ---
DEADBAND_PX = 25          # no movement if within this many pixels from center
KP = 0.015                # proportional gain: pixels -> degrees
MAX_STEP_DEG = 3          # cap per update
MIN_AREA = 400            # reject tiny blobs
SERVO_DT = 0.05           # 20 Hz servo updates

last_servo_t = 0.0
kernel = np.ones((5, 5), np.uint8)

try:
    while True:
        frame = picam.capture_array()

        # If you intended flip to match physical mounting, keep it.
        # (0 = vertical flip; -1 = both axes)
        frame = cv2.flip(frame, 0)

        # Smooth image a bit before thresholding
        frame_blur = cv2.GaussianBlur(frame, (5, 5), 0)

        # IMPORTANT: frame is RGB888 => use RGB2HSV
        frame_hsv = cv2.cvtColor(frame_blur, cv2.COLOR_RGB2HSV)

        # Read trackbar values safely each loop
        hue_low  = cv2.getTrackbarPos("hue_low",  "My trackbars")
        hue_high = cv2.getTrackbarPos("hue_high", "My trackbars")
        sat_low  = cv2.getTrackbarPos("sat_low",  "My trackbars")
        sat_high = cv2.getTrackbarPos("sat_high", "My trackbars")
        val_low  = cv2.getTrackbarPos("val_low",  "My trackbars")
        val_high = cv2.getTrackbarPos("val_high", "My trackbars")
        #print(hue_low, hue_high, sat_low, sat_high, val_low, val_high)
        lower = np.array([hue_low,  sat_low,  val_low], dtype=np.uint8)
        upper = np.array([hue_high, sat_high, val_high], dtype=np.uint8)

        mask = cv2.inRange(frame_hsv, lower, upper)

        # Clean the mask (remove specks + fill small holes)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)

        contours, _hier = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(contour)

            if area > MIN_AREA:
                x, y, w, h = cv2.boundingRect(contour)
                cx = x + w / 2
                cy = y + h / 2

                # Draw box + center
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.circle(frame, (int(cx), int(cy)), 5, (255, 0, 0), -1)

                # Error relative to center of image
                err_x = cx - (displ_w / 2)
                err_y = cy - (displ_h / 2)

                # Rate-limit servo commands
                now = time.time()
                if now - last_servo_t >= SERVO_DT:
                    last_servo_t = now

                    # Only move if outside deadband
                    d_pan = 0.0
                    d_tilt = 0.0

                    if abs(err_x) > DEADBAND_PX:
                        d_pan = clamp(KP * err_x, -MAX_STEP_DEG, MAX_STEP_DEG)

                    if abs(err_y) > DEADBAND_PX:
                        d_tilt = clamp(KP * err_y, -MAX_STEP_DEG, MAX_STEP_DEG)

                    # Update angles (sign might need flipping depending on your mounting)
                    pan_angle  = clamp(pan_angle  + d_pan,  PAN_MIN,  PAN_MAX)
                    tilt_angle = clamp(tilt_angle + d_tilt, TILT_MIN, TILT_MAX)

                    goto(pan_angle, tilt_angle)

        cv2.imshow("Camera", frame)
        # Optional: show mask for tuning
        # cv2.imshow("Mask", mask)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    picam.stop()
    picam.close()
    cv2.destroyAllWindows()
    print("All is closed")
