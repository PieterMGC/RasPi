import cv2
import time
import numpy as np
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


def update_fps(
    frame_count: int,
    last_time: float,
    fps: float,
    interval: float = 0.5,
) -> tuple[int, float, float]:
    now = time.perf_counter()
    elapsed = now - last_time

    if elapsed >= interval:
        fps = frame_count / elapsed
        frame_count = 0
        last_time = now

    return frame_count, last_time, fps


def draw_metrics_window(fps: float, window_name: str = "Metrics") -> None:
    # Small black image
    img = np.zeros((50, 120, 3), dtype=np.uint8)

    cv2.putText(
        img,
        f"FPS: {fps:.1f}",
        (20, 30), #x,y position
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5, # ← TEXT SCALE (this controls size)
        (0, 255, 0),
        1, # ← LINE THICKNESS
        cv2.LINE_AA,
    )

    cv2.imshow(window_name, img)


def run_preview(picam: Picamera2) -> None:
    camera_win = "Camera"
    metrics_win = "Metrics"

    cv2.namedWindow(camera_win, cv2.WINDOW_NORMAL)
    cv2.namedWindow(metrics_win, cv2.WINDOW_AUTOSIZE)

    # --- Window placement ---
    cam_x, cam_y = 500, 500           # top-left corner of Camera
    cam_width = 640                 # must match camera width
    gap = 0                        # space between windows

    cv2.moveWindow(camera_win, cam_x, cam_y)
    cv2.moveWindow(metrics_win, cam_x + cam_width + gap, cam_y)
    frame_count = 0
    fps = 0.0
    last_time = time.perf_counter()

    while True:
        frame = picam.capture_array()
        frame_count += 1

        frame = cv2.flip(frame, -1)

        frame_count, last_time, fps = update_fps(
            frame_count, last_time, fps
        )

        cv2.imshow("Camera", frame)
        draw_metrics_window(fps)

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

    picam = setup_camera(640, 360, 30)

    try:
        run_preview(picam)
    finally:
        cleanup(picam)


if __name__ == "__main__":
    main()
