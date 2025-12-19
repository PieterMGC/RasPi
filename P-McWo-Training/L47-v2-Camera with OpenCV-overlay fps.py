import cv2
import time
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


def update_fps(frame_count: int, last_time: float, fps: float, interval: float = 0.5,) -> tuple[int, float, float]:
    """
    Update FPS value every `interval` seconds.

    Returns:
        updated_frame_count, updated_last_time, updated_fps
    """
    now = time.perf_counter()
    elapsed = now - last_time

    if elapsed >= interval:
        fps = frame_count / elapsed
        frame_count = 0
        last_time = now

    return frame_count, last_time, fps


def draw_fps(frame, fps: float, pos=(10, 30)) -> None:
    cv2.putText(frame, f"FPS: {fps:.1f}", pos, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA,)


def run_preview(picam: Picamera2, window_name: str = "Camera", flip: bool = True) -> None:
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    frame_count = 0
    fps = 0.0
    last_time = time.perf_counter()

    while True:
        frame = picam.capture_array()
        frame_count += 1
        if flip:
            frame = cv2.flip(frame, -1)
        frame_count, last_time, fps = update_fps(frame_count, last_time, fps)
        draw_fps(frame, fps)
        cv2.imshow(window_name, frame)
        if (cv2.waitKey(1) & 0xFF) == ord("q"):
            break


def cleanup(picam: Picamera2) -> None:
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
        run_preview(picam, flip=True)
    finally:
        cleanup(picam)


if __name__ == "__main__":
    main()
