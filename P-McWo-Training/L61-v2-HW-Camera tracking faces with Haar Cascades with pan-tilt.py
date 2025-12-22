import cv2
from picamera2 import Picamera2
from adafruit_servokit import ServoKit
from time import sleep

width, height, fps = 640, 360, 30

DETECT_SCALE = 0.5
FACE_XML = "./haar/haarcascade_frontalface_default.xml"

kit = ServoKit(channels=16)
TILT = 0
PAN = 1
# Safe movement limits
PAN_MIN, PAN_MAX = 40, 140
TILT_MIN, TILT_MAX = 60, 120

pan_angle = 90
tilt_angle = 90

def setup_opencv() -> None:
    cv2.setUseOptimized(True)
    print("OpenCV:", cv2.__version__)
    print("Optimized:", cv2.useOptimized())

def setup_haar(xml_path: str = FACE_XML) -> cv2.CascadeClassifier:
    face_cascade = cv2.CascadeClassifier(xml_path)

    if face_cascade.empty():
        raise FileNotFoundError(f"Face cascade not loaded: {xml_path}")

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

def setup_pan_tilt() -> None:
    # Tune per your hardware
    kit.servo[TILT].set_pulse_width_range(500, 2500)  # tilt
    kit.servo[PAN].set_pulse_width_range(500, 2500)  # pan
    goto(pan_angle, tilt_angle)
    
def goto(pan_angle, tilt_angle, pause=0.1):
    kit.servo[PAN].angle = pan_angle
    kit.servo[TILT].angle = tilt_angle
    sleep(pause)

def detect_face(frame_rgb, face_cascade, scale = DETECT_SCALE):
    frame_gray = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2GRAY)
    frame_gray_small = cv2.resize(frame_gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    #frame_temp = cv2.equalizeHist(frame_temp)
    faces_small = face_cascade.detectMultiScale(frame_gray_small,scaleFactor=1.2,minNeighbors=5,minSize=(24, 24))
    # Terugschalen naar originele coördinaten
    inv = 1.0 / scale
    faces = [(int(x * inv), int(y * inv), int(w * inv), int(h * inv)) for (x, y, w, h) in faces_small]
    return faces

def draw_face(frame_rgb, faces) -> None:
    for (x, y, w, h) in faces:
        cv2.rectangle(frame_rgb, (x, y), (x + w, y + h), (255, 0, 0), 2)
        
def calculate_pantilt_angle(faces):
    for (x, y, w, h) in faces:
        error_w = (x+w/2)-width/2
        error_h = (y+h/2)-height/2
        if abs(error_w) > 25 and (pan_angle < PAN_MAX or pan_angle > PAN_MIN):
            pan_angle += error_w/70
        if abs(error_h) > 25 and (tilt_angle < TILT_MAX or tilt_angle > TILT_MIN):
            tilt_angle += error_h/70
    return pan_angle, tilt_angle
    
def run_preview(picam: Picamera2, face_cascade, window_name: str = "Camera", flip: bool = True, detect: bool = True, track: bool = True) -> None:
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    while True:
        frame = picam.capture_array()

        if flip:
            frame = cv2.flip(frame, -1)
        if detect:
            last_faces = detect_face(frame, face_cascade, scale=DETECT_SCALE)
            draw_face(frame, last_faces)
        if track and len(last_faces) > 0:    
            pan_angle, tilt_angle = calculate_pantilt_angle(last_faces)
            goto(pan_angle, titl_angle)

        cv2.imshow(window_name, frame)
        
        if (cv2.waitKey(1) & 0xFF) == ord("q"):
            break


def cleanup(picam: Picamera2) -> None:
    # Safe even if already stopped/closing
    try:
        goto(90, 90)
    except Exception:
        pass    
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
    setup_pan_tilt()

    width, height, fps = 640, 360, 30
    pan_angle = 90

    picam = setup_camera(width, height, fps)

    try:
        run_preview(picam, face_cascade, window_name="Camera", flip=True, detect=True, track=True)
    finally:
        cleanup(picam)


if __name__ == "__main__":
    main()

