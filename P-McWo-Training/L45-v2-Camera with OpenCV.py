import cv2
from picamera2 import Picamera2


def setup_opencv() -> None:
    cv2.setUseOptimized(True)
    print("OpenCV:", cv2.__version__)
    print("Optimized:", cv2.useOptimized())


def setup_camera(width: int, height: int, fps: int) -> Picamera2:
    picam = Picamera2()
    cfg = picam.create_preview_configuration(
        main={"size": (width, height), "format": "RGB888"},
        controls={"FrameRate": fps},
    )
    picam.configure(cfg)
    picam.start()
    return picam


def run_preview(picam: Picamera2, window_name: str = "Camera", flip: bool = True) -> None:
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    while True:
        frame = picam.capture_array()

        if flip:
            frame = cv2.flip(frame, -1)

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

    width, height, fps = 640, 360, 30
    picam = setup_camera(width, height, fps)

    try:
        run_preview(picam, window_name="Camera", flip=True)
    finally:
        cleanup(picam)


if __name__ == "__main__":
    main()