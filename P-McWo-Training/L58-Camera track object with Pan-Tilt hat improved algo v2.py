import cv2
import numpy as np
import time
from picamera2 import Picamera2
from adafruit_servokit import ServoKit
from time import sleep

print(cv2.__version__)

displ_w = 640
displ_h = 360

kit = ServoKit(channels=16)

TILT = 0
PAN = 1

kit.servo[TILT].set_pulse_width_range(500, 2500)
kit.servo[PAN].set_pulse_width_range(500, 2500)

PAN_MIN, PAN_MAX = 40, 140
TILT_MIN, TILT_MAX = 60, 120

def clamp(v, vmin, vmax):
    return max(vmin, min(vmax, v))

def nothing(_):
    pass

def goto(pan_angle, tilt_angle, pause=0.05):
    kit.servo[PAN].angle = pan_angle
    kit.servo[TILT].angle = tilt_angle
    sleep(pause)

# --- Camera ---
picam = Picamera2()
picam.preview_configuration.main.size = (displ_w, displ_h)
picam.preview_configuration.main.format = "RGB888"
picam.preview_configuration.controls.FrameRate = 60
picam.preview_configuration.align()
picam.configure("preview")
picam.start()

# --- Trackbars (yellow defaults) ---
cv2.namedWindow("My trackbars")
cv2.createTrackbar("hue_low",    "My trackbars", 85, 179, nothing)
cv2.createTrackbar("hue_high",   "My trackbars", 95, 179, nothing)
cv2.createTrackbar("sat_low",    "My trackbars", 100, 255, nothing)
cv2.createTrackbar("sat_high",   "My trackbars", 255, 255, nothing)
cv2.createTrackbar("value_low",  "My trackbars", 100, 255, nothing)
cv2.createTrackbar("value_high", "My trackbars", 255, 255, nothing)

# --- Initial position ---
pan_angle = 90.0
tilt_angle = 90.0
goto(pan_angle, tilt_angle)

kernel = np.ones((5, 5), np.uint8)

# --- Tracking / control parameters ---
MIN_AREA = 500                 # ignore tiny blobs
EMA_ALPHA = 0.30               # 0.2 smoother, 0.4 more responsive
DEADBAND = 0.06                # normalized error (≈ 6% of half-screen)
KP_PAN = 12.0                  # deg per normalized error per update
KP_TILT = 12.0
MAX_STEP = 3.0                 # deg per update cap
SERVO_DT = 0.05                # 20 Hz servo updates
LOST_TIMEOUT = 0.5             # seconds before "lost" behavior

cx_f = None
cy_f = None
last_servo_t = 0.0
last_seen_t = time.time()

try:
    while True:
        frame = picam.capture_array()
        frame = cv2.flip(frame, 0)

        # Pre-filter
        frame_blur = cv2.GaussianBlur(frame, (5, 5), 0)
        hsv = cv2.cvtColor(frame_blur, cv2.COLOR_RGB2HSV)

        # Read trackbars
        hue_low  = cv2.getTrackbarPos("hue_low", "My trackbars")
        hue_high = cv2.getTrackbarPos("hue_high", "My trackbars")
        sat_low  = cv2.getTrackbarPos("sat_low", "My trackbars")
        sat_high = cv2.getTrackbarPos("sat_high", "My trackbars")
        val_low  = cv2.getTrackbarPos("value_low", "My trackbars")
        val_high = cv2.getTrackbarPos("value_high", "My trackbars")

        lower = np.array([hue_low, sat_low, val_low], dtype=np.uint8)
        upper = np.array([hue_high, sat_high, val_high], dtype=np.uint8)

        # Mask + cleanup
        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        found = False
        if contours:
            contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(contour)

            if area >= MIN_AREA:
                found = True
                last_seen_t = time.time()

                # Centroid (more stable than bounding box center)
                M = cv2.moments(contour)
                if M["m00"] > 0:
                    cx = M["m10"] / M["m00"]
                    cy = M["m01"] / M["m00"]
                else:
                    found = False

                if found:
                    # EMA smoothing
                    if cx_f is None:
                        cx_f, cy_f = cx, cy
                    else:
                        cx_f = EMA_ALPHA * cx + (1 - EMA_ALPHA) * cx_f
                        cy_f = EMA_ALPHA * cy + (1 - EMA_ALPHA) * cy_f

                    # Draw for debug
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    cv2.circle(frame, (int(cx_f), int(cy_f)), 5, (255, 0, 0), -1)

        # --- Control + servo update (rate-limited) ---
        now = time.time()
        if now - last_servo_t >= SERVO_DT:
            last_servo_t = now

            if found and cx_f is not None:
                # Normalized error in [-1..+1]
                err_x = (cx_f - displ_w / 2) / (displ_w / 2)
                err_y = (cy_f - displ_h / 2) / (displ_h / 2)

                # Deadband
                if abs(err_x) < DEADBAND:
                    err_x = 0.0
                if abs(err_y) < DEADBAND:
                    err_y = 0.0

                # Proportional step with cap
                d_pan = clamp(KP_PAN * err_x, -MAX_STEP, MAX_STEP)
                d_tilt = clamp(KP_TILT * err_y, -MAX_STEP, MAX_STEP)

                # Apply (flip sign here if motion is reversed)
                pan_angle = clamp(pan_angle + d_pan, PAN_MIN, PAN_MAX)
                tilt_angle = clamp(tilt_angle + d_tilt, TILT_MIN, TILT_MAX)

                kit.servo[PAN].angle = pan_angle
                kit.servo[TILT].angle = tilt_angle

            else:
                # Object lost: hold position; optionally drift back to center after timeout
                if (now - last_seen_t) > LOST_TIMEOUT:
                    # gentle return to center (comment out if you prefer "hold forever")
                    pan_angle = pan_angle + clamp((90 - pan_angle) * 0.05, -1.0, 1.0)
                    tilt_angle = tilt_angle + clamp((90 - tilt_angle) * 0.05, -1.0, 1.0)
                    pan_angle = clamp(pan_angle, PAN_MIN, PAN_MAX)
                    tilt_angle = clamp(tilt_angle, TILT_MIN, TILT_MAX)
                    kit.servo[PAN].angle = pan_angle
                    kit.servo[TILT].angle = tilt_angle

        cv2.imshow("Camera", frame)
        # cv2.imshow("Mask", mask)  # uncomment when tuning HSV

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    goto(90, 90)
    picam.stop()
    picam.close()
    cv2.destroyAllWindows()
    print("All is closed")
