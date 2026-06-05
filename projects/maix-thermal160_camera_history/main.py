import logging
import math
import os
import struct
import time
from array import array
from typing import Tuple
 
import cv2
import numpy as np
from maix import app, display, gpio, image, pinmap, touchscreen
from maix.peripheral import uart
from maix.sys import device_name


PMOD_W = 160
PMOD_H = 120
FRAME_PIXEL_SIZE = PMOD_W * PMOD_H
FRAME_TAIL_SIZE = 30
FRAME_BODY_SIZE = FRAME_PIXEL_SIZE + FRAME_TAIL_SIZE
INT16_MAX = 0x7FFF

BAUDRATE_INIT = 2000000
BAUDRATE_HIGH = 4000000
UART_BUFFER_SIZE = 32768
UART_READ_TIMEOUT_MS = 10

SKIP_COUNT = 10
STARTUP_GRACE_SEC = 3.0
SAMPLE_INTERVAL_SEC = 1.0
DISPLAY_REFRESH_SEC = 0.25
LIVE_WINDOW_SEC = 30.0 * 60.0
RUN_TARGET_SEC = 24.0 * 3600.0

APP_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
OUTPUT_DIR = os.path.join(APP_DIR, "output")
CSV_FLUSH_EVERY = 10

THERMAL_RESET_PIN = "A9"
THERMAL_RESET_GPIO = "GPIOA9"
THERMAL_RESET_IDLE_LEVEL = 1
THERMAL_RESET_ACTIVE_LEVEL = 0
THERMAL_RESET_ASSERT_SEC = 0.12
THERMAL_RESET_RELEASE_DELAY_SEC = 0.40

RGB_BLACK = (0, 0, 0)
RGB_BG = (14, 16, 20)
RGB_PANEL = (28, 31, 38)
RGB_GRID = (62, 68, 78)
RGB_WHITE = (235, 238, 242)
RGB_MUTED = (148, 156, 168)
RGB_RED = (255, 120, 120)
RGB_GREEN = (125, 210, 145)
RGB_CYAN = (95, 205, 245)
RGB_YELLOW = (245, 210, 95)
RGB_BLUE = (100, 150, 255)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
_thermal_reset_gpio = None


def is_in_button(x: int, y: int, btn_pos: Tuple[int, int, int, int]) -> bool:
    return (btn_pos[0] < x < btn_pos[0] + btn_pos[2] and
            btn_pos[1] < y < btn_pos[1] + btn_pos[3])


def ensure_dir(path: str) -> None:
    try:
        os.makedirs(path, exist_ok=True)
    except TypeError:
        if not os.path.exists(path):
            os.makedirs(path)
    except OSError:
        pass


def stamp() -> str:
    try:
        return time.strftime("%Y%m%d_%H%M%S")
    except Exception:
        return str(int(time.time()))


def finite(v) -> bool:
    try:
        return v == v and abs(v) != float("inf")
    except Exception:
        return False


def fmt_float(v, digits: int = 2) -> str:
    if not finite(v):
        return "nan"
    return ("%." + str(digits) + "f") % v


class HardwareHAL:
    _PORT_REGISTRY = {
        "MaixCAM2": "/dev/ttyS2",
        "MaixCAM": None,
        "MaixCAM-Pro": None,
    }
    _device = ""

    @classmethod
    def serial_port(cls) -> str:
        dn = device_name()
        if not isinstance(dn, str) or not dn.strip():
            raise TypeError("Invalid device identifier received: '%s'" % dn)
        port = cls._PORT_REGISTRY.get(dn)
        if port is None:
            raise RuntimeError("Platform mismatch: Device '%s' is not supported" % dn)
        cls._device = dn
        return port


def pulse_thermal_reset() -> None:
    global _thermal_reset_gpio
    if HardwareHAL._device != "MaixCAM2":
        return
    try:
        ret = pinmap.set_pin_function(THERMAL_RESET_PIN, THERMAL_RESET_GPIO)
        if ret != 0:
            logger.warning(
                "Thermal160 reset pinmap returned %s for %s -> %s",
                ret, THERMAL_RESET_PIN, THERMAL_RESET_GPIO,
            )
        _thermal_reset_gpio = gpio.GPIO(THERMAL_RESET_GPIO, gpio.Mode.OUT)
        _thermal_reset_gpio.value(THERMAL_RESET_IDLE_LEVEL)
        time.sleep(0.02)
        _thermal_reset_gpio.value(THERMAL_RESET_ACTIVE_LEVEL)
        time.sleep(THERMAL_RESET_ASSERT_SEC)
        _thermal_reset_gpio.value(THERMAL_RESET_IDLE_LEVEL)
        time.sleep(THERMAL_RESET_RELEASE_DELAY_SEC)
        logger.info("Thermal160 reset pulse sent on %s", THERMAL_RESET_PIN)
    except Exception as exc:
        logger.warning("Thermal160 reset pulse skipped: %s", exc)


def open_thermal_uart():
    devices = uart.list_devices()
    if not devices:
        raise RuntimeError("No available UART devices found")

    port_name = HardwareHAL.serial_port()
    pulse_thermal_reset()
    serial = uart.UART(port=port_name, baudrate=BAUDRATE_INIT)
    if HardwareHAL._device == "MaixCAM2":
        serial.write(b"\x44")
        serial.close()
        time.sleep(0.1)
        serial = uart.UART(port=port_name, baudrate=BAUDRATE_HIGH)
    return serial


def read_uart(serial, size: int, timeout_ms: int):
    try:
        return serial.read(size, timeout=timeout_ms)
    except TypeError:
        return serial.read(size, timeout_ms)


def telemetry_plausible(body: bytes) -> bool:
    if len(body) != FRAME_BODY_SIZE:
        return False
    telemetry = body[FRAME_PIXEL_SIZE:]
    raw_vtemp = struct.unpack_from(">H", telemetry, 0)[0]
    if raw_vtemp & 0xC000:
        return False

    t_lo_x10 = struct.unpack_from(">h", telemetry, 2)[0]
    t_hi_x10 = struct.unpack_from(">h", telemetry, 4)[0]
    if t_lo_x10 == INT16_MAX and t_hi_x10 == INT16_MAX:
        return True
    if not (-1000 <= t_lo_x10 <= 3200):
        return False
    if not (-1000 <= t_hi_x10 <= 3200):
        return False
    if t_hi_x10 < t_lo_x10:
        return False
    return True


def parse_frame_body(body: bytes):
    telemetry = body[FRAME_PIXEL_SIZE:]
    pixels = np.frombuffer(body[:FRAME_PIXEL_SIZE], dtype=np.uint8).reshape(PMOD_H, PMOD_W)
    return {
        "pixels": pixels,
        "vtemp": struct.unpack_from(">H", telemetry, 0)[0] & 0x3FFF,
        "t_lo_x10": struct.unpack_from(">h", telemetry, 2)[0],
        "t_hi_x10": struct.unpack_from(">h", telemetry, 4)[0],
        "anchor": struct.unpack_from(">i", telemetry, 6)[0],
        "smooth_low": struct.unpack_from(">H", telemetry, 10)[0],
        "smooth_high": struct.unpack_from(">H", telemetry, 12)[0],
        "mean_diff": struct.unpack_from(">f", telemetry, 14)[0],
        "ntc_ref": struct.unpack_from(">H", telemetry, 18)[0],
        "ntc": struct.unpack_from(">H", telemetry, 20)[0],
        "nuc_decision": telemetry[22],
        "nuc_count": telemetry[23],
        "nuc_dg": struct.unpack_from(">h", telemetry, 24)[0],
        "nuc_dv": struct.unpack_from(">h", telemetry, 26)[0],
        "nuc_dn": struct.unpack_from(">h", telemetry, 28)[0],
    }


def drain_latest_frame(buffer: bytearray, skip: int, frame_count: int):
    latest = None
    while True:
        idx = buffer.find(b"\xFF")
        if idx < 0:
            buffer.clear()
            break

        end = idx + 1 + FRAME_BODY_SIZE
        if len(buffer) < end:
            if idx > 0:
                del buffer[:idx]
            break

        body = bytes(buffer[idx + 1:end])
        if not telemetry_plausible(body):
            del buffer[:idx + 1]
            continue

        if len(buffer) > end and buffer[end] != 0xFF:
            del buffer[:idx + 1]
            continue

        del buffer[:end]
        frame_count += 1
        if skip <= SKIP_COUNT:
            skip += 1
            continue
        latest = parse_frame_body(body)

    return latest, skip, frame_count


def safe_colormap(name: str, fallback_id: int):
    cp = getattr(cv2, name, fallback_id)
    test = np.arange(256, dtype=np.uint8).reshape(1, 256)
    try:
        cv2.applyColorMap(test, cp)
        return cp
    except Exception:
        return None


def build_lut():
    cp = safe_colormap("COLORMAP_TURBO", 20)
    if cp is None:
        cp = safe_colormap("COLORMAP_HOT", 0)
    if cp is None:
        raise RuntimeError("No supported OpenCV colormap")
    gray = np.arange(256, dtype=np.uint8).reshape(1, 256)
    colored = cv2.applyColorMap(gray, cp)
    return cv2.cvtColor(colored, cv2.COLOR_BGR2RGB).reshape(256, 3)


def fpa_to_celsius(vtemp: int) -> float:
    if vtemp == 0:
        return float("nan")
    return 25.0 + (vtemp - 8192) / 70.0


def ntc_adu_to_celsius(adc: int) -> float:
    if adc <= 0 or adc >= 4095:
        return float("nan")
    r_ntc = 10000.0 * adc / (4095.0 - adc)
    inv_t = 1.0 / 298.15 + math.log(r_ntc / 10000.0) / 3435.0
    return 1.0 / inv_t - 273.15


def u8_to_temp(u8_value: int, t_lo: float, t_hi: float) -> float:
    return t_lo + (t_hi - t_lo) * min(max(float(u8_value) / 254.0, 0.0), 1.0)


def frame_to_sample(frame, elapsed_s: float):
    t_lo_x10 = frame["t_lo_x10"]
    t_hi_x10 = frame["t_hi_x10"]
    calibrated = (t_lo_x10 != INT16_MAX and
                  t_hi_x10 != INT16_MAX and
                  t_hi_x10 > t_lo_x10)

    t_lo = float("nan")
    t_hi = float("nan")
    scene_mid = float("nan")
    center = float("nan")
    min_temp = float("nan")
    max_temp = float("nan")

    if calibrated:
        t_lo = t_lo_x10 / 10.0
        t_hi = t_hi_x10 / 10.0
        scene_mid = (t_lo + t_hi) / 2.0
        pixels = frame["pixels"]
        center = u8_to_temp(int(pixels[PMOD_H // 2, PMOD_W // 2]), t_lo, t_hi)
        min_temp = u8_to_temp(int(pixels.min()), t_lo, t_hi)
        max_temp = u8_to_temp(int(pixels.max()), t_lo, t_hi)

    return {
        "t": elapsed_s,
        "scene_mid": scene_mid,
        "center": center,
        "min": min_temp,
        "max": max_temp,
        "fpa": fpa_to_celsius(frame["vtemp"]),
        "ntc": ntc_adu_to_celsius(frame["ntc"]),
        "t_lo": t_lo,
        "t_hi": t_hi,
        "vtemp": frame["vtemp"],
        "ntc_adu": frame["ntc"],
        "anchor": frame["anchor"],
        "smooth_low": frame["smooth_low"],
        "smooth_high": frame["smooth_high"],
        "mean_diff": frame["mean_diff"],
        "nuc_decision": frame["nuc_decision"],
        "nuc_count": frame["nuc_count"],
        "nuc_dg": frame["nuc_dg"],
        "nuc_dv": frame["nuc_dv"],
        "nuc_dn": frame["nuc_dn"],
    }


class HistoryStore:
    def __init__(self):
        self.t = array("f")
        self.scene_mid = array("f")
        self.center = array("f")
        self.fpa = array("f")
        self.ntc = array("f")
        self.min = array("f")
        self.max = array("f")

    def append(self, sample) -> None:
        self.t.append(float(sample["t"]))
        self.scene_mid.append(float(sample["scene_mid"]))
        self.center.append(float(sample["center"]))
        self.fpa.append(float(sample["fpa"]))
        self.ntc.append(float(sample["ntc"]))
        self.min.append(float(sample["min"]))
        self.max.append(float(sample["max"]))

    def __len__(self) -> int:
        return len(self.t)


class CsvLogger:
    def __init__(self, out_dir: str):
        ensure_dir(out_dir)
        self.path = os.path.join(out_dir, "history_%s.csv" % stamp())
        self._file = open(self.path, "w")
        self._count = 0
        self._file.write(
            "elapsed_s,scene_mid_c,center_c,min_c,max_c,fpa_c,ntc_c,"
            "t_lo_c,t_hi_c,vtemp_adu,ntc_adu,anchor,smooth_low,smooth_high,"
            "mean_diff,nuc_decision,nuc_count,nuc_dg,nuc_dv,nuc_dn\n"
        )
        self._file.flush()

    def write(self, sample) -> None:
        row = [
            fmt_float(sample["t"], 3),
            fmt_float(sample["scene_mid"], 3),
            fmt_float(sample["center"], 3),
            fmt_float(sample["min"], 3),
            fmt_float(sample["max"], 3),
            fmt_float(sample["fpa"], 3),
            fmt_float(sample["ntc"], 3),
            fmt_float(sample["t_lo"], 3),
            fmt_float(sample["t_hi"], 3),
            str(sample["vtemp"]),
            str(sample["ntc_adu"]),
            str(sample["anchor"]),
            str(sample["smooth_low"]),
            str(sample["smooth_high"]),
            fmt_float(sample["mean_diff"], 3),
            str(sample["nuc_decision"]),
            str(sample["nuc_count"]),
            str(sample["nuc_dg"]),
            str(sample["nuc_dv"]),
            str(sample["nuc_dn"]),
        ]
        self._file.write(",".join(row) + "\n")
        self._count += 1
        if self._count % CSV_FLUSH_EVERY == 0:
            self._file.flush()

    def close(self) -> None:
        self._file.flush()
        self._file.close()


def draw_text(canvas, text: str, x: int, y: int, color=RGB_WHITE, scale: float = 0.45, thickness: int = 1):
    cv2.putText(canvas, text, (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX,
                scale, color, thickness)


def text_size(text: str, scale: float = 0.45, thickness: int = 1):
    size, baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, thickness)
    return size[0], size[1], baseline


def draw_centered_text(canvas, text: str, rect, color=RGB_WHITE,
                       scale: float = 0.45, thickness: int = 1):
    x, y, w, h = rect
    tw, th, _ = text_size(text, scale, thickness)
    tx = x + max(0, (w - tw) // 2)
    ty = y + max(th + 1, (h + th) // 2 - 1)
    draw_text(canvas, text, tx, ty, color, scale, thickness)


def latest_valid(values):
    for i in range(len(values) - 1, -1, -1):
        v = values[i]
        if finite(v):
            return v
    return float("nan")


def compact_text(text: str, max_chars: int) -> str:
    if not text or max_chars <= 0:
        return ""
    if len(text) <= max_chars:
        return text
    if max_chars <= 3:
        return text[:max_chars]
    return text[:max_chars - 3] + "..."


def fit_text_width(text: str, max_width: int, scale: float = 0.45, thickness: int = 1) -> str:
    if not text or max_width <= 0:
        return ""
    if text_size(text, scale, thickness)[0] <= max_width:
        return text
    suffix = "..."
    for length in range(len(text) - 1, 0, -1):
        candidate = text[:length] + suffix
        if text_size(candidate, scale, thickness)[0] <= max_width:
            return candidate
    return ""


def compact_saved_msg(saved_msg: str, max_chars: int = 28) -> str:
    if not saved_msg:
        return ""
    if saved_msg.startswith("saved "):
        saved_msg = "saved " + os.path.basename(saved_msg[6:])
    return compact_text(saved_msg, max_chars)


def compact_status(status: str) -> str:
    if status.startswith("recording "):
        return "REC " + status[10:]
    if status.startswith("initializing thermal160"):
        return "INIT" + status[len("initializing thermal160"):]
    if status == "thermal160 device not found":
        return "DEVICE NOT FOUND"
    return status


def draw_hud_corners(canvas, rect):
    x0, y0, w, h = rect
    n = max(10, min(20, w // 8, h // 4))
    for sx, sy in ((x0, y0), (x0 + w, y0), (x0, y0 + h), (x0 + w, y0 + h)):
        dx = 1 if sx == x0 else -1
        dy = 1 if sy == y0 else -1
        cv2.line(canvas, (sx, sy), (sx + dx * n, sy), RGB_CYAN, 1)
        cv2.line(canvas, (sx, sy), (sx, sy + dy * n), RGB_CYAN, 1)


def finite_range_multi(series_list, start: int, end: int):
    lo = None
    hi = None
    for values in series_list:
        for i in range(start, end):
            v = values[i]
            if not finite(v):
                continue
            if lo is None or v < lo:
                lo = v
            if hi is None or v > hi:
                hi = v
    if lo is None:
        return None
    if hi <= lo:
        lo -= 0.5
        hi += 0.5
    else:
        pad = max(0.3, (hi - lo) * 0.10)
        lo -= pad
        hi += pad
    return lo, hi


def nice_ticks(lo: float, hi: float, count: int = 4):
    if not finite(lo) or not finite(hi) or hi <= lo:
        return []
    if count <= 1:
        return [lo]
    return [lo + (hi - lo) * i / (count - 1) for i in range(count)]


def x_label(seconds: float) -> str:
    if seconds < 3600.0:
        return "%.0fm" % (seconds / 60.0)
    return "%.1fh" % (seconds / 3600.0)


def draw_axis_ticks(canvas, rect, t0: float, t1: float, left_rng, right_rng):
    x0, y0, w, h = rect
    for k in range(5):
        x = x0 + int(w * k / 4)
        cv2.line(canvas, (x, y0), (x, y0 + h), RGB_GRID, 1)
        label_t = t0 + (t1 - t0) * k / 4
        draw_text(canvas, x_label(label_t), x - 14, y0 + h + 16, RGB_MUTED, 0.34)

    for tick in nice_ticks(left_rng[0], left_rng[1], 4):
        y = y0 + h - 1 - int((tick - left_rng[0]) / (left_rng[1] - left_rng[0]) * (h - 1))
        cv2.line(canvas, (x0, y), (x0 + w, y), RGB_GRID, 1)
        draw_text(canvas, fmt_float(tick, 1), max(0, x0 - 42), y + 4, RGB_RED, 0.34)

    if right_rng is not None:
        for tick in nice_ticks(right_rng[0], right_rng[1], 4):
            y = y0 + h - 1 - int((tick - right_rng[0]) / (right_rng[1] - right_rng[0]) * (h - 1))
            draw_text(canvas, fmt_float(tick, 1), x0 + w + 6, y + 4, RGB_GREEN, 0.34)


def draw_series(canvas, rect, times, values, start: int, end: int,
                value_range, color, max_points: int):
    if value_range is None:
        return
    x0, y0, w, h = rect
    t0 = times[start]
    t1 = times[end - 1]
    if t1 <= t0:
        t1 = t0 + 1.0
    v0, v1 = value_range
    step = max(1, int((end - start) / max_points))

    prev = None
    for i in range(start, end, step):
        v = values[i]
        if not finite(v):
            prev = None
            continue
        x = x0 + int((times[i] - t0) / (t1 - t0) * (w - 1))
        y = y0 + h - 1 - int((v - v0) / (v1 - v0) * (h - 1))
        pt = (x, y)
        if prev is not None:
            cv2.line(canvas, prev, pt, color, 1)
        prev = pt


def draw_chart(canvas, rect, history: HistoryStore, window_sec, max_points: int):
    x0, y0, w, h = rect
    cv2.rectangle(canvas, (x0, y0), (x0 + w, y0 + h), RGB_PANEL, -1)
    cv2.rectangle(canvas, (x0, y0), (x0 + w, y0 + h), RGB_GRID, 1)

    if len(history) < 2:
        draw_text(canvas, "Waiting for samples...", x0 + 10, y0 + h // 2, RGB_MUTED, 0.55)
        return

    end = len(history)
    start = 0
    if window_sec is not None:
        threshold = history.t[end - 1] - window_sec
        while start < end - 1 and history.t[start] < threshold:
            start += 1

    if end - start < 2:
        draw_text(canvas, "Waiting for samples...", x0 + 10, y0 + h // 2, RGB_MUTED, 0.55)
        return

    left_rng = finite_range_multi([history.fpa, history.ntc], start, end)
    right_rng = finite_range_multi([history.scene_mid, history.center], start, end)
    if left_rng is None and right_rng is None:
        draw_text(canvas, "Waiting for valid temperature samples...", x0 + 10, y0 + h // 2, RGB_MUTED, 0.55)
        return
    if left_rng is None:
        left_rng = right_rng

    plot_rect = (x0 + 48, y0 + 30, w - 96, h - 62)
    px, py, pw, ph = plot_rect
    cv2.rectangle(canvas, (px, py), (px + pw, py + ph), RGB_BLACK, -1)

    t0 = history.t[start]
    t1 = history.t[end - 1]
    if t1 <= t0:
        t1 = t0 + 1.0
    draw_axis_ticks(canvas, plot_rect, t0, t1, left_rng, right_rng)

    draw_series(canvas, plot_rect, history.t, history.fpa, start, end, left_rng, RGB_RED, max_points)
    draw_series(canvas, plot_rect, history.t, history.ntc, start, end, left_rng, RGB_CYAN, max_points)
    if right_rng is not None:
        draw_series(canvas, plot_rect, history.t, history.scene_mid, start, end, right_rng, RGB_BLUE, max_points)
        draw_series(canvas, plot_rect, history.t, history.center, start, end, right_rng, RGB_GREEN, max_points)

    cv2.rectangle(canvas, (px, py), (px + pw, py + ph), RGB_GRID, 1)

    draw_text(canvas, "FPA/NTC C", px, y0 + 18, RGB_RED, 0.42)
    draw_text(canvas, "scene/center C", px + pw - 118, y0 + 18, RGB_GREEN, 0.42)

    legend_x = px + 8
    legend_y = py + 18
    legend = [
        ("FPA", latest_valid(history.fpa), RGB_RED),
        ("NTC", latest_valid(history.ntc), RGB_CYAN),
        ("scene", latest_valid(history.scene_mid), RGB_BLUE),
        ("center", latest_valid(history.center), RGB_GREEN),
    ]
    for label, val, color in legend:
        text = "%s %sC" % (label, fmt_float(val, 1))
        draw_text(canvas, text, legend_x, legend_y, color, 0.42)
        legend_x += max(74, len(text) * 8)

    span = history.t[end - 1] - history.t[start]
    draw_text(canvas, "window %.0f min" % (span / 60.0), px + pw - 104, py + ph - 8, RGB_MUTED, 0.36)


def render_preview(canvas, frame, rect, lut, color_buf):
    x0, y0, w, h = rect
    cv2.rectangle(canvas, (x0, y0), (x0 + w, y0 + h), RGB_PANEL, -1)
    if frame is None:
        draw_text(canvas, "No frame", x0 + 18, y0 + h // 2, RGB_MUTED, 0.65)
        return

    gray = cv2.flip(frame["pixels"], -1)
    np.take(lut, gray, axis=0, out=color_buf)
    preview = cv2.resize(color_buf, (w, h), interpolation=cv2.INTER_LINEAR)
    canvas[y0:y0 + h, x0:x0 + w, :] = preview
    cv2.rectangle(canvas, (x0, y0), (x0 + w, y0 + h), RGB_GRID, 1)


def draw_status_panel(canvas, rect, sample, csv_path: str, status: str, saved_msg: str):
    x0, y0, w, h = rect
    cv2.rectangle(canvas, (x0, y0), (x0 + w, y0 + h), RGB_PANEL, -1)
    cv2.rectangle(canvas, (x0, y0), (x0 + w, y0 + h), RGB_GRID, 1)
    draw_hud_corners(canvas, rect)

    elapsed = ""
    if sample is not None:
        elapsed = "%.1fh/%.0fh" % (sample["t"] / 3600.0, RUN_TARGET_SEC / 3600.0)
    elapsed_w = text_size(elapsed, 0.46, 1)[0] + 10 if elapsed and w >= 250 else 0
    status_text = compact_status(status)
    status_text = fit_text_width(status_text, w - elapsed_w - 18, 0.55, 2)
    draw_text(canvas, status_text, x0 + 8, y0 + 24, RGB_WHITE, 0.55, 2)
    if elapsed_w:
        draw_text(canvas, elapsed, x0 + w - elapsed_w + 2, y0 + 24, RGB_MUTED, 0.46)
    cv2.line(canvas, (x0 + 8, y0 + 36), (x0 + w - 8, y0 + 36), RGB_GRID, 1)
    cv2.line(canvas, (x0 + 8, y0 + 38), (x0 + max(9, w // 3), y0 + 38), RGB_BLUE, 1)

    if sample is None:
        draw_text(canvas, fit_text_width("Waiting for samples", w - 18, 0.56, 1),
                  x0 + 10, y0 + 70, RGB_MUTED, 0.56)
        return

    main = "CENTER %sC" % fmt_float(sample["center"], 1)
    draw_text(canvas, fit_text_width(main, w - 18, 0.90, 2), x0 + 10, y0 + 74,
              RGB_GREEN, 0.90, 2)

    gauge_y = y0 + 84
    gauge_x0 = x0 + 10
    gauge_x1 = x0 + w - 10
    cv2.line(canvas, (gauge_x0, gauge_y), (gauge_x1, gauge_y), RGB_GRID, 1)
    if finite(sample["min"]) and finite(sample["max"]) and sample["max"] > sample["min"]:
        marker = int((sample["center"] - sample["min"]) /
                     (sample["max"] - sample["min"]) * (gauge_x1 - gauge_x0))
        marker = max(0, min(gauge_x1 - gauge_x0, marker))
        mx = gauge_x0 + marker
        cv2.line(canvas, (gauge_x0, gauge_y), (mx, gauge_y), RGB_GREEN, 2)
        cv2.line(canvas, (mx, gauge_y - 4), (mx, gauge_y + 4), RGB_CYAN, 1)

    center_line = "SCENE %sC   MIN %sC   MAX %sC" % (
        fmt_float(sample["scene_mid"], 1),
        fmt_float(sample["min"], 1),
        fmt_float(sample["max"], 1),
    )
    draw_text(canvas, fit_text_width(center_line, w - 18, 0.43, 1),
              x0 + 10, y0 + 106, RGB_MUTED, 0.43)

    telemetry_line = "FPA %sC   NTC %sC" % (
        fmt_float(sample["fpa"], 1),
        fmt_float(sample["ntc"], 1),
    )
    if h >= 122:
        draw_text(canvas, fit_text_width(telemetry_line, w - 18, 0.40, 1),
                  x0 + 10, y0 + 124, RGB_CYAN, 0.40)

    if h >= 142:
        msg = fit_text_width(compact_saved_msg(saved_msg, 48), w - 20, 0.36, 1)
        if msg:
            draw_text(canvas, msg, x0 + 10, y0 + h - 10, RGB_BLUE, 0.36)


def render_screen(width: int, height: int, history: HistoryStore, frame, sample,
                  csv_path: str, status: str, saved_msg: str, lut, color_buf,
                  back_rect, save_rect):
    canvas = np.zeros((height, width, 3), dtype=np.uint8)
    canvas[:, :, :] = RGB_BG

    cv2.rectangle(canvas, (back_rect[0], back_rect[1]),
                  (back_rect[0] + back_rect[2], back_rect[1] + back_rect[3]), RGB_PANEL, -1)
    cv2.rectangle(canvas, (save_rect[0], save_rect[1]),
                  (save_rect[0] + save_rect[2], save_rect[1] + save_rect[3]), RGB_BLUE, -1)
    draw_centered_text(canvas, "BACK", back_rect, RGB_WHITE, 0.64, 2)
    draw_centered_text(canvas, "SAVE", save_rect, RGB_WHITE, 0.64, 2)
    title_x = back_rect[0] + back_rect[2] + 12
    title = fit_text_width("TN160 history", save_rect[0] - title_x - 8, 0.66, 2)
    draw_text(canvas, title, title_x, 25, RGB_WHITE, 0.66, 2)

    top = max(back_rect[3], save_rect[3]) + 8
    preview_h = max(112, int((height - top) * 0.40))
    preview_w = max(132, int(width * 0.32))
    if width - preview_w - 24 < 250:
        preview_w = max(112, width - 274)
    preview_rect = (8, top, preview_w, preview_h)
    status_rect = (preview_rect[0] + preview_rect[2] + 8, top,
                   width - preview_rect[2] - 24, preview_h)
    chart_rect = (8, top + preview_h + 8, width - 16, height - top - preview_h - 14)

    render_preview(canvas, frame, preview_rect, lut, color_buf)
    draw_status_panel(canvas, status_rect, sample, csv_path, status, saved_msg)
    draw_chart(canvas, chart_rect, history, LIVE_WINDOW_SEC, max(120, width * 2))
    return canvas


def render_history_png(history: HistoryStore, csv_path: str, path: str) -> bool:
    if len(history) < 2:
        return False
    width, height = 1400, 780
    canvas = np.zeros((height, width, 3), dtype=np.uint8)
    canvas[:, :, :] = RGB_BG
    draw_text(canvas, "TN160 temperature history", 28, 42, RGB_WHITE, 0.8, 2)
    draw_text(canvas, "samples %d   elapsed %.2f h   csv %s" %
              (len(history), history.t[-1] / 3600.0, csv_path),
              28, 76, RGB_MUTED, 0.5)
    draw_chart(canvas, (28, 108, width - 56, height - 150),
               history, None, max(1000, width * 3))

    ensure_dir(os.path.dirname(path) or ".")
    bgr = cv2.cvtColor(canvas, cv2.COLOR_RGB2BGR)
    return bool(cv2.imwrite(path, bgr))


def save_png(history: HistoryStore, csv_path: str):
    ensure_dir(OUTPUT_DIR)
    path = os.path.join(OUTPUT_DIR, "trend_%s.png" % stamp())
    if render_history_png(history, csv_path, path):
        return path
    return None


def show_error_page(disp, message: str) -> None:
    w, h = disp.width(), disp.height()
    canvas = np.zeros((h, w, 3), dtype=np.uint8)
    canvas[:, :, :] = RGB_BLACK
    draw_text(canvas, message, max(8, w // 2 - 150), h // 2, RGB_WHITE, 0.55)
    disp.show(image.cv2image(canvas, bgr=False, copy=True))


def main() -> None:
    disp = display.Display()
    disp.set_hmirror(False)
    disp.set_vflip(True)
    ts = touchscreen.TouchScreen()

    width, height = disp.width(), disp.height()
    button_h = max(32, height // 11)
    back_rect = [0, 0, max(68, width // 8), button_h]
    save_rect = [width - max(76, width // 7), 0, max(76, width // 7), button_h]

    lut = build_lut()
    color_buf = np.zeros((PMOD_H, PMOD_W, 3), dtype=np.uint8)
    history = HistoryStore()
    serial = None
    csv_log = None

    try:
        serial = open_thermal_uart()
    except Exception as exc:
        logger.error("UART init failed: %s", exc)
        show_error_page(disp, "thermal160 UART init failed")
        time.sleep(3.0)
        return

    csv_log = CsvLogger(OUTPUT_DIR)

    buffer = bytearray()
    skip = 0
    frame_count = 0
    latest_frame = None
    latest_sample = None
    last_frame_time = None
    last_sample_time = 0.0
    last_draw_time = 0.0
    last_touch_time = 0.0
    saved_msg = ""
    t_start = time.time()

    logger.info("History CSV: %s", csv_log.path)

    try:
        while not app.need_exit():
            now = time.time()
            x, y, pressed = ts.read()
            if pressed and now - last_touch_time > 0.35:
                last_touch_time = now
                if is_in_button(x, y, back_rect):
                    app.set_exit_flag(True)
                    break
                if is_in_button(x, y, save_rect):
                    path = save_png(history, csv_log.path)
                    if path:
                        saved_msg = "saved " + path
                        logger.info("Saved trend PNG: %s", path)
                    else:
                        saved_msg = "not enough samples"

            chunk = read_uart(serial, UART_BUFFER_SIZE, UART_READ_TIMEOUT_MS)
            if chunk:
                buffer.extend(bytes(chunk))
                frame, skip, frame_count = drain_latest_frame(buffer, skip, frame_count)
                if frame is not None:
                    latest_frame = frame
                    last_frame_time = now

            if latest_frame is not None and now - last_sample_time >= SAMPLE_INTERVAL_SEC:
                latest_sample = frame_to_sample(latest_frame, now - t_start)
                history.append(latest_sample)
                csv_log.write(latest_sample)
                last_sample_time = now

            if now - last_draw_time >= DISPLAY_REFRESH_SEC:
                elapsed = now - t_start
                if last_frame_time is None:
                    if elapsed < STARTUP_GRACE_SEC:
                        dots = "." * ((int(elapsed * 3.0) % 3) + 1)
                        status = "initializing thermal160" + dots
                    else:
                        status = "thermal160 device not found"
                else:
                    age = now - last_frame_time
                    if age > 2.0:
                        status = "no new frame %.1fs" % age
                    else:
                        status = "recording %.1ffps" % (frame_count / max(elapsed, 0.001))

                canvas = render_screen(width, height, history, latest_frame, latest_sample,
                                       csv_log.path, status, saved_msg, lut, color_buf,
                                       back_rect, save_rect)
                disp.show(image.cv2image(canvas, bgr=False, copy=True))
                last_draw_time = now

    except Exception as exc:
        logger.error("Fatal: %s", exc)
        raise
    finally:
        if csv_log is not None:
            try:
                csv_log.close()
            except Exception:
                pass
        if serial is not None:
            serial.close()
        if csv_log is not None and len(history) >= 2:
            path = save_png(history, csv_log.path)
            if path:
                logger.info("Saved exit trend PNG: %s", path)


if __name__ == "__main__":
    main()
