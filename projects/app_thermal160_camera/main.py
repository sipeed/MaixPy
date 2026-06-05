import logging
import struct
import time
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
FPS_WINDOW_SIZE = 30
EMA_ALPHA = 0.2

BACK_BUTTON_WIDTH_RATIO = 0.1
DEFAULT_ICON_PATH = "/maixapp/share/icon/ret.png"

FONT_SCALE = 2.0
CENTER_TEMP_SCALE = 1.1
CORNER_TEMP_SCALE = 0.9

THERMAL_RESET_PIN = "A9"
THERMAL_RESET_GPIO = "GPIOA9"
THERMAL_RESET_IDLE_LEVEL = 1
THERMAL_RESET_ACTIVE_LEVEL = 0
THERMAL_RESET_ASSERT_SEC = 0.12
THERMAL_RESET_RELEASE_DELAY_SEC = 0.40


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
_thermal_reset_gpio = None


def is_in_button(x: int, y: int, btn_pos: Tuple[int, int, int, int]) -> bool:
    return (btn_pos[0] < x < btn_pos[0] + btn_pos[2] and
            btn_pos[1] < y < btn_pos[1] + btn_pos[3])


def draw_label(img_disp: image.Image, x: int, y: int, text: str, color, scale: float = 0.8) -> None:
    img_disp.draw_string(x + 1, y + 1, text, image.COLOR_BLACK, scale=scale)
    img_disp.draw_string(x, y, text, color, scale=scale)


def draw_cross(img_disp: image.Image, x: int, y: int, color, size: int = 12) -> None:
    img_disp.draw_line(x - size, y, x + size, y, color)
    img_disp.draw_line(x, y - size, x, y + size, color)


def get_back_btn_img(width: int) -> Tuple[image.Image, int, int]:
    ret_width = int(width * BACK_BUTTON_WIDTH_RATIO)
    img_back = image.load(DEFAULT_ICON_PATH)
    w, h = (ret_width, img_back.height() * ret_width // img_back.width())
    if w % 2:
        w += 1
    if h % 2:
        h += 1
    img_back = img_back.resize(w, h)
    img_back = img_back.rotate(0)
    return img_back, w, h


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


def pixels_to_temp(pixels: np.ndarray, t_lo: float, t_hi: float) -> np.ndarray:
    if t_hi <= t_lo:
        return np.full_like(pixels, t_lo, dtype=np.float32)
    norm = (pixels.astype(np.float32) / 254.0).clip(0.0, 1.0)
    return (t_lo + (t_hi - t_lo) * norm).astype(np.float32)


def safe_colormap(name: str, fallback_id: int):
    cp = getattr(cv2, name, fallback_id)
    test = np.arange(256, dtype=np.uint8).reshape(1, 256)
    try:
        cv2.applyColorMap(test, cp)
        return (name.replace("COLORMAP_", "").lower(), cp)
    except Exception:
        return None


def build_colormap_options():
    options = []
    for name, fallback in [
        ("COLORMAP_TURBO", 20),
        ("COLORMAP_HOT", 0),
        ("COLORMAP_COOL", 1),
        ("COLORMAP_DEEPGREEN", 15),
        ("COLORMAP_MAGMA", 13),
    ]:
        entry = safe_colormap(name, fallback)
        if entry:
            options.append(entry)
    if not options:
        raise RuntimeError("No supported OpenCV colormap")
    return options


def get_cv2_lut(cmap_entry):
    _, cp = cmap_entry
    gray = np.arange(256, dtype=np.uint8).reshape(1, 256)
    colored = cv2.applyColorMap(gray, cp)
    return cv2.cvtColor(colored, cv2.COLOR_BGR2RGB).reshape(256, 3)


def init_text_button(width: int, height: int, label: str) -> image.Image:
    btn = image.Image(width, height, image.Format.FMT_RGB888)
    btn.draw_rect(0, 0, width, height, image.COLOR_BLACK, -1)
    text_x = max(2, (width - len(label) * 6) // 2)
    text_y = max(2, (height - 15) // 2)
    btn.draw_string(text_x, text_y, label, image.COLOR_WHITE, scale=0.6)
    return btn.rotate(0)


def draw_wait_page(disp, img_back, img_cmap, elapsed: float, has_error: bool) -> None:
    w, h = disp.width(), disp.height()
    main_img = image.Image(w, h, image.Format.FMT_RGB888)
    main_img.draw_rect(0, 0, w, h, image.COLOR_BLACK, -1)

    if has_error:
        title = "thermal160 device not found"
    else:
        title = "Initializing thermal160"

    char_w = 10 * FONT_SCALE
    char_h = 20 * FONT_SCALE
    x_msg = int((w - len(title) * char_w) // 2)
    y_msg = int((h - char_h) // 2) - 18
    main_img.draw_string(x_msg + 1, y_msg + 1, title, image.COLOR_BLACK, scale=FONT_SCALE)
    main_img.draw_string(x_msg, y_msg, title, image.COLOR_WHITE, scale=FONT_SCALE)

    if not has_error:
        bar_w = max(80, int(w * 0.58))
        bar_h = max(8, int(h * 0.035))
        bar_x = (w - bar_w) // 2
        bar_y = y_msg + int(char_h) + 22
        progress = max(0.0, min(elapsed / STARTUP_GRACE_SEC, 1.0))
        fill_w = int((bar_w - 4) * progress)
        main_img.draw_rect(bar_x, bar_y, bar_w, bar_h, image.COLOR_WHITE, 1)
        if fill_w > 0:
            main_img.draw_rect(bar_x + 2, bar_y + 2, fill_w, bar_h - 4, image.COLOR_WHITE, -1)

    main_img.draw_image(0, 0, img_back)
    if img_cmap is not None:
        main_img.draw_image(w - img_cmap.width(), h - img_cmap.height(), img_cmap)
    disp.show(main_img)


def nuc_status_text(frame) -> str:
    decision = frame.get("nuc_decision", 255)
    count = frame.get("nuc_count", 0)
    dg = frame.get("nuc_dg", 0)
    if decision == 1:
        return "NUC ACC#%d dg%+d" % (count, dg)
    if decision == 2:
        return "NUC REJ_DG dg%+d" % dg
    if decision == 3:
        return "NUC REJ_JMP dg%+d" % dg
    return "NUC --"


def main() -> None:
    disp = display.Display()
    disp.set_hmirror(False)
    disp.set_vflip(True)
    ts = touchscreen.TouchScreen()

    img_back, img_back_w, img_back_h = get_back_btn_img(disp.width())
    back_rect = [0, 0, img_back_w, img_back_h]
    cmap_rect = [disp.width() - img_back_w, disp.height() - img_back_h, img_back_w, img_back_h]

    cmap_options = build_colormap_options()
    cmap_idx = 0
    cmap_abbrev = {"hot": "HOT", "cool": "COOL", "deepgreen": "DGRN", "magma": "MAGM", "turbo": "TRBO"}

    def current_cmap_button():
        name = cmap_options[cmap_idx][0]
        label = cmap_abbrev.get(name, name[:5].upper())
        return init_text_button(img_back_w, img_back_h, label)

    img_cmap = current_cmap_button()
    lut = get_cv2_lut(cmap_options[cmap_idx])
    color_buf = np.zeros((PMOD_H, PMOD_W, 3), dtype=np.uint8)

    disp_w, disp_h = disp.width(), disp.height()
    disp_buffers = [
        np.zeros((disp_h, disp_w, 3), dtype=np.uint8),
        np.zeros((disp_h, disp_w, 3), dtype=np.uint8),
    ]
    db_idx = 0

    try:
        serial = open_thermal_uart()
    except Exception as exc:
        logger.error("UART init failed: %s", exc)
        draw_wait_page(disp, img_back, img_cmap, STARTUP_GRACE_SEC, True)
        time.sleep(3.0)
        return

    buffer = bytearray()
    skip = 0
    frame_count = 0
    frame_timestamps = []
    fps_ema = 0.0
    capture_started = False
    t_start = time.time()
    last_wait_draw = 0.0

    logger.info("System: Maix test pipeline initialized.")

    try:
        while not app.need_exit():
            x, y, pressed = ts.read()
            if pressed and is_in_button(x, y, back_rect):
                app.set_exit_flag(True)
                break

            if pressed and is_in_button(x, y, cmap_rect):
                cmap_idx = (cmap_idx + 1) % len(cmap_options)
                lut = get_cv2_lut(cmap_options[cmap_idx])
                img_cmap = current_cmap_button()
                time.sleep(0.2)

            chunk = read_uart(serial, UART_BUFFER_SIZE, UART_READ_TIMEOUT_MS)
            if chunk:
                buffer.extend(bytes(chunk))
                latest, skip, frame_count = drain_latest_frame(buffer, skip, frame_count)
            else:
                latest = None

            if latest is None:
                if not capture_started:
                    now = time.time()
                    elapsed = now - t_start
                    if now - last_wait_draw >= 0.15:
                        draw_wait_page(disp, img_back, img_cmap, elapsed, elapsed >= STARTUP_GRACE_SEC)
                        last_wait_draw = now
                continue

            if not capture_started:
                logger.info("System: First valid frame received.")
            capture_started = True

            gray_np = cv2.flip(latest["pixels"], -1)
            t_lo_x10 = latest["t_lo_x10"]
            t_hi_x10 = latest["t_hi_x10"]
            has_temp = (
                t_lo_x10 != INT16_MAX and
                t_hi_x10 != INT16_MAX and
                t_hi_x10 > t_lo_x10
            )

            disp_buffer = disp_buffers[db_idx]
            gray_blurred = cv2.GaussianBlur(gray_np, (3, 3), 1)
            np.take(lut, gray_blurred, axis=0, out=color_buf)
            cv2.resize(color_buf, (disp_w, disp_h), dst=disp_buffer, interpolation=cv2.INTER_LINEAR)

            img_disp = image.cv2image(disp_buffer, bgr=False, copy=False)
            center_x = disp_w // 2
            center_y = disp_h // 2
            draw_cross(img_disp, center_x, center_y, image.COLOR_WHITE, 14)

            if has_temp:
                t_lo = t_lo_x10 / 10.0
                t_hi = t_hi_x10 / 10.0
                temp_img = pixels_to_temp(gray_np, t_lo, t_hi)
                min_idx = np.argmin(temp_img)
                max_idx = np.argmax(temp_img)
                min_y, min_x = np.unravel_index(min_idx, temp_img.shape)
                max_y, max_x = np.unravel_index(max_idx, temp_img.shape)
                sx = disp_w / PMOD_W
                sy = disp_h / PMOD_H

                draw_cross(img_disp, int(max_x * sx), int(max_y * sy), image.COLOR_RED, 12)
                draw_cross(img_disp, int(min_x * sx), int(min_y * sy), image.COLOR_BLUE, 12)

                center_temp = temp_img[PMOD_H // 2, PMOD_W // 2]
                draw_label(
                    img_disp,
                    min(max(center_x + 18, 8), disp_w - 96),
                    min(max(center_y - 18, 8), disp_h - 24),
                    "%.1fC" % center_temp,
                    image.COLOR_WHITE,
                    scale=CENTER_TEMP_SCALE,
                )
                text_x = 8
                text_y = disp_h - 104
                draw_label(img_disp, text_x, text_y, "MAX %.1fC" % temp_img[max_y, max_x],
                           image.COLOR_RED, scale=CORNER_TEMP_SCALE)
                draw_label(img_disp, text_x, text_y + 24, "MIN %.1fC" % temp_img[min_y, min_x],
                           image.COLOR_BLUE, scale=CORNER_TEMP_SCALE)
                draw_label(img_disp, text_x, text_y + 48, "RNG %.1f~%.1fC" % (t_lo, t_hi),
                           image.COLOR_WHITE, scale=0.85)
                draw_label(img_disp, text_x, text_y + 72, nuc_status_text(latest),
                           image.COLOR_WHITE, scale=0.65)
            else:
                draw_label(img_disp, 8, disp_h - 32, "UNCALIBRATED", image.COLOR_WHITE, scale=0.9)

            img_disp.draw_image(0, 0, img_back)
            img_disp.draw_image(disp_w - img_back_w, disp_h - img_back_h, img_cmap)
            disp.show(img_disp)
            db_idx ^= 1

            current_time = time.time()
            frame_timestamps.append(current_time)
            if len(frame_timestamps) > FPS_WINDOW_SIZE:
                frame_timestamps.pop(0)
            if len(frame_timestamps) > 1:
                window_duration = frame_timestamps[-1] - frame_timestamps[0]
                if window_duration > 0:
                    window_fps = (len(frame_timestamps) - 1) / window_duration
                    if fps_ema == 0.0:
                        fps_ema = window_fps
                    else:
                        fps_ema = EMA_ALPHA * window_fps + (1.0 - EMA_ALPHA) * fps_ema
                    if frame_count % 10 == 0:
                        logger.info("FPS: %.2f", fps_ema)

    except Exception as exc:
        logger.error("Fatal: %s", exc)
        raise
    finally:
        if serial is not None:
            serial.close()
            logger.info("System: UART closed.")


if __name__ == "__main__":
    main()
