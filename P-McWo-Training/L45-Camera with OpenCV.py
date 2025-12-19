import cv2
from picamera2 import Picamera2

print("OpenCV:", cv2.__version__)
cv2.setUseOptimized(True)
print("Optimized:", cv2.useOptimized())

# Tune these first for Raspberry Pi efficiency
DISPL_W = 640
DISPL_H = 360
FPS = 30

picam = Picamera2()

# Configure preview stream
cfg = picam.create_preview_configuration(
    main={"size": (DISPL_W, DISPL_H), "format": "RGB888"},
    controls={"FrameRate": FPS},
)
picam.configure(cfg)
picam.start()

WINDOW = "Camera"
cv2.namedWindow(WINDOW, cv2.WINDOW_NORMAL)

try:
    while True:
        frame = picam.capture_array()
        frame = cv2.flip(frame, -1)
        cv2.imshow(WINDOW, frame)
        # Use & 0xFF for compatibility across platforms/backends
        if (cv2.waitKey(1) & 0xFF) == ord("q"):
            break
finally:
    picam.stop()
    picam.close()
    cv2.destroyAllWindows()
    print("All is closed")
