import cv2
from picamera2 import Picamera2

DETECT_SCALE = 0.5

def setup_opencv() -> None:
    cv2.setUseOptimized(True)
    print("OpenCV:", cv2.__version__)
    print("Optimized:", cv2.useOptimized())

def setup_haar():
    face_cascade = cv2.CascadeClassifier('./haar/haarcascade_frontalface_default.xml')

    if face_cascade.empty():
        raise FileNotFoundError(f"Face cascade not loaded: {FACE_XML}")

    return face_cascade

def setup_camera(width: int, height: int, fps: int) -> Picamera2:
    picam = Picamera2()
    cfg = picam.create_preview_configuration(
        main={"size": (width, height), "format": "RGB888"},
        controls={"FrameRate": fps},
    )
    picam.configure(cfg)
    picam.start()
    return picam

def detect_face(frame, face_cascade):
    global DETECT_SCALE
    frame_temp = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame_temp = cv2.resize(frame_temp, None, fx=DETECT_SCALE, fy=DETECT_SCALE, interpolation=cv2.INTER_LINEAR)
    frame_temp = cv2.equalizeHist(frame_temp)
    faces = face_cascade.detectMultiScale(frame_temp,scaleFactor=1.3,minNeighbors=5,minSize=(30, 30))
    # Terugschalen naar originele coördinaten
    inv = 1.0 / DETECT_SCALE
    for (sx, sy, sw, sh) in faces:
        x = int(sx * inv)
        y = int(sy * inv)
        w = int(sw * inv)
        h = int(sh * inv)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
    return frame

def run_preview(picam: Picamera2, face_cascade, window_name: str = "Camera", flip: bool = True, detect: bool = True) -> None:
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    while True:
        frame = picam.capture_array()

        if flip:
            frame = cv2.flip(frame, -1)
        if detect:
            frame = detect_face(frame, face_cascade)

        cv2.imshow(window_name, frame)
        
        if (cv2.waitKey(1) & 0xFF) == ord("q"):
            break


def cleanup(picam: Picamera2) -> None:
    # Safe even if already stopped/closing
    try:
        picam.stop()
    except Exception:
        pass
    try:
        picam.close()
    except Exception:
        pass
    cv2.destroyAllWindows()
    print("All is closed")


def main() -> None:
    setup_opencv()
    face_cascade = setup_haar()

    width, height, fps = 640, 360, 30

    picam = setup_camera(width, height, fps)

    try:
        run_preview(picam, face_cascade, window_name="Camera", flip=True, detect=True)
    finally:
        cleanup(picam)


if __name__ == "__main__":
    main()
