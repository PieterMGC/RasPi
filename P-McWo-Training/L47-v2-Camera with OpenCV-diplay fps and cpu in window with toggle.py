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


def read_cpu_temp_c() -> float | None:
    """
    Raspberry Pi CPU temp (°C) from sysfs.
    Returns None if unavailable.
    """
    path = "/sys/class/thermal/thermal_zone0/temp"
    try:
        with open(path, "r") as f:
            milli_c = int(f.read().strip())
        return milli_c / 1000.0
    except Exception:
        return None


def update_cpu_temp(
    last_read_time: float,
    cached_temp: float | None,
    interval: float = 1.0,
) -> tuple[float, float | None]:
    """
    Updates CPU temp at most once per `interval` seconds.
    Returns: new_last_read_time, new_cached_temp
    """
    now = time.perf_counter()
    if (now - last_read_time) >= interval:
        return now, read_cpu_temp_c()
    return last_read_time, cached_temp


def draw_metrics_window(
    fps: float,
    cpu_temp_c: float | None,
    show_fps: bool,
    show_temp: bool,
    window_name: str = "Metrics",
) -> None:
    img = np.zeros((120, 260, 3), dtype=np.uint8)

    y = 40
    if show_fps:
        cv2.putText(
            img, f"FPS: {fps:.1f}", (15, y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA
        )
        y += 40

    if show_temp:
        temp_str = f"{cpu_temp_c:.1f} C" if cpu_temp_c is not None else "n/a"
        cv2.putText(
            img, f"CPU: {temp_str}", (15, y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA
        )

    # Small hint line
    cv2.putText(
        img, "F=FPS  T=Temp  Q=Quit", (15, 112),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA
    )

    cv2.imshow(window_name, img)


def run_preview(picam: Picamera2, cam_width: int, flip: bool = True) -> None:
    camera_win = "Camera"
    metrics_win = "Metrics"

    cv2.namedWindow(camera_win, cv2.WINDOW_NORMAL)
    cv2.namedWindow(metrics_win, cv2.WINDOW_AUTOSIZE)

    # Place Metrics next to Camera
    cam_x, cam_y = 50, 50
    gap = 10
    cv2.moveWindow(camera_win, cam_x, cam_y)
    cv2.moveWindow(metrics_win, cam_x + cam_width + gap, cam_y)

    # Toggles (runtime)
    show_fps = True
    show_temp = True

    # FPS state
    frame_count = 0
    fps = 0.0
    last_fps_time = time.perf_counter()

    # Temp state (cached, update 1x/sec)
    last_temp_time = 0.0
    cpu_temp_c = None

    while True:
        frame = picam.capture_array()
        frame_count += 1

        if flip:
            frame = cv2.flip(frame, -1)

        # Update metrics cheaply
        frame_count, last_fps_time, fps = update_fps(frame_count, last_fps_time, fps, interval=0.5)
        last_temp_time, cpu_temp_c = update_cpu_temp(last_temp_time, cpu_temp_c, interval=1.0)

        # Show windows
        cv2.imshow(camera_win, frame)
        draw_metrics_window(fps, cpu_temp_c, show_fps, show_temp, window_name=metrics_win)

        # Key handling (works when Metrics window is focused too)
        k = cv2.waitKey(1) & 0xFF
        if k == ord("q"):
            break
        elif k == ord("f"):
            show_fps = not show_fps
        elif k == ord("t"):
            show_temp = not show_temp


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
        run_preview(picam, cam_width=width, flip=True)
    finally:
        cleanup(picam)


if __name__ == "__main__":
    main()
