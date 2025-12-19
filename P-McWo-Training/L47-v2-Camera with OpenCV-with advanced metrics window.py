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


# ---------- FPS ----------
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


# ---------- CPU temp ----------
def read_cpu_temp_c() -> float | None:
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
    now = time.perf_counter()
    if (now - last_read_time) >= interval:
        return now, read_cpu_temp_c()
    return last_read_time, cached_temp


# ---------- CPU load % (from /proc/stat deltas) ----------
def _read_proc_stat_cpu() -> tuple[int, int] | None:
    """
    Returns (total_jiffies, idle_jiffies) from /proc/stat for the aggregate CPU line.
    """
    try:
        with open("/proc/stat", "r") as f:
            line = f.readline()
        parts = line.split()
        if not parts or parts[0] != "cpu":
            return None
        # cpu user nice system idle iowait irq softirq steal guest guest_nice
        values = [int(x) for x in parts[1:]]
        total = sum(values)
        idle = values[3] + (values[4] if len(values) > 4 else 0)  # idle + iowait
        return total, idle
    except Exception:
        return None


def update_cpu_load(
    last_read_time: float,
    cached_load: float | None,
    prev_total: int | None,
    prev_idle: int | None,
    interval: float = 0.5,
) -> tuple[float, float | None, int | None, int | None]:
    """
    CPU load percentage based on jiffies between reads.
    Returns: new_last_time, new_load, new_prev_total, new_prev_idle
    """
    now = time.perf_counter()
    if (now - last_read_time) < interval:
        return last_read_time, cached_load, prev_total, prev_idle

    cur = _read_proc_stat_cpu()
    if cur is None:
        return now, None, prev_total, prev_idle

    cur_total, cur_idle = cur
    if prev_total is None or prev_idle is None:
        # First sample: cannot compute a delta yet
        return now, cached_load, cur_total, cur_idle

    dt_total = cur_total - prev_total
    dt_idle = cur_idle - prev_idle

    if dt_total <= 0:
        load = cached_load
    else:
        load = (1.0 - (dt_idle / dt_total)) * 100.0

    return now, load, cur_total, cur_idle


# ---------- RAM usage (from /proc/meminfo) ----------
def read_ram_usage() -> tuple[int, int, float] | None:
    """
    Returns (used_mb, total_mb, used_percent) using MemTotal and MemAvailable.
    """
    try:
        memtotal_kb = None
        memavail_kb = None
        with open("/proc/meminfo", "r") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    memtotal_kb = int(line.split()[1])
                elif line.startswith("MemAvailable:"):
                    memavail_kb = int(line.split()[1])
                if memtotal_kb is not None and memavail_kb is not None:
                    break

        if memtotal_kb is None or memavail_kb is None or memtotal_kb <= 0:
            return None

        used_kb = memtotal_kb - memavail_kb
        total_mb = memtotal_kb // 1024
        used_mb = used_kb // 1024
        used_pct = (used_kb / memtotal_kb) * 100.0
        return used_mb, total_mb, used_pct
    except Exception:
        return None


def update_ram_usage(
    last_read_time: float,
    cached_ram: tuple[int, int, float] | None,
    interval: float = 1.0,
) -> tuple[float, tuple[int, int, float] | None]:
    now = time.perf_counter()
    if (now - last_read_time) >= interval:
        return now, read_ram_usage()
    return last_read_time, cached_ram


# ---------- Metrics window ----------
def draw_metrics_window(
    fps: float,
    cpu_temp_c: float | None,
    cpu_load_pct: float | None,
    ram: tuple[int, int, float] | None,
    show_fps: bool,
    show_temp: bool,
    show_cpu: bool,
    show_ram: bool,
    window_name: str = "Metrics",
) -> None:
    # Auto height based on enabled rows (keeps window tidy)
    rows = sum([show_fps, show_temp, show_cpu, show_ram])
    height = 60 + rows * 35 + 25
    width = 400
    img = np.zeros((height, width, 3), dtype=np.uint8)

    y = 40
    if show_fps:
        cv2.putText(img, f"FPS: {fps:.1f}", (15, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2, cv2.LINE_AA)
        y += 35

    if show_temp:
        temp_str = f"{cpu_temp_c:.1f} C" if cpu_temp_c is not None else "n/a"
        cv2.putText(img, f"CPU Temp: {temp_str}", (15, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2, cv2.LINE_AA)
        y += 35

    if show_cpu:
        load_str = f"{cpu_load_pct:.1f} %" if cpu_load_pct is not None else "n/a"
        cv2.putText(img, f"CPU Load: {load_str}", (15, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2, cv2.LINE_AA)
        y += 35

    if show_ram:
        if ram is None:
            ram_str = "n/a"
        else:
            used_mb, total_mb, used_pct = ram
            ram_str = f"{used_mb}/{total_mb} MB ({used_pct:.1f}%)"
        cv2.putText(img, f"RAM: {ram_str}", (15, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2, cv2.LINE_AA)
        y += 35

    cv2.putText(img, "F=FPS  T=Temp  C=CPU  R=RAM  Q=Quit", (15, height - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

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

    # Runtime toggles
    show_fps = True
    show_temp = True
    show_cpu = True
    show_ram = True

    # FPS state
    frame_count = 0
    fps_val = 0.0
    last_fps_time = time.perf_counter()

    # Temp state
    last_temp_time = 0.0
    cpu_temp_c = None

    # CPU load state
    last_cpu_time = 0.0
    cpu_load_pct = None
    prev_total = None
    prev_idle = None

    # RAM state
    last_ram_time = 0.0
    ram = None

    while True:
        frame = picam.capture_array()
        frame_count += 1

        if flip:
            frame = cv2.flip(frame, -1)

        # Update FPS cheaply
        frame_count, last_fps_time, fps_val = update_fps(frame_count, last_fps_time, fps_val, interval=0.5)

        # Update other metrics (rate-limited)
        if show_temp:
            last_temp_time, cpu_temp_c = update_cpu_temp(last_temp_time, cpu_temp_c, interval=1.0)

        if show_cpu:
            last_cpu_time, cpu_load_pct, prev_total, prev_idle = update_cpu_load(
                last_cpu_time, cpu_load_pct, prev_total, prev_idle, interval=0.5
            )

        if show_ram:
            last_ram_time, ram = update_ram_usage(last_ram_time, ram, interval=1.0)

        # Display windows
        cv2.imshow(camera_win, frame)
        draw_metrics_window(
            fps=fps_val,
            cpu_temp_c=cpu_temp_c,
            cpu_load_pct=cpu_load_pct,
            ram=ram,
            show_fps=show_fps,
            show_temp=show_temp,
            show_cpu=show_cpu,
            show_ram=show_ram,
            window_name=metrics_win,
        )

        # Key handling (works when Metrics window is focused too)
        k = cv2.waitKey(1) & 0xFF
        if k == ord("q"):
            break
        elif k == ord("f"):
            show_fps = not show_fps
        elif k == ord("t"):
            show_temp = not show_temp
        elif k == ord("c"):
            show_cpu = not show_cpu
        elif k == ord("r"):
            show_ram = not show_ram


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
