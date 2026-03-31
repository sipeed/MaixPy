import logging
import time
from typing import Tuple

import numpy as np
from maix import app, image, display, touchscreen
from maix.peripheral import uart
from maix.sys import device_name

PMOD_W = 160
PMOD_H = 120
FRAME_SIZE = PMOD_W * PMOD_H
SKIP_COUNT = 10
CMAP = True  # 渲染管线分支路由开关：True为热成像伪彩映射，False为原生灰度零拷贝

# 配置常量
BAUDRATE_INIT = 2000000
BAUDRATE_HIGH = 4000000
FPS_WINDOW_SIZE = 30
EMA_ALPHA = 0.2
SERIAL_TIMEOUT = 1
FONT_SCALE = 2.0

# UART 配置
UART_BUFFER_SIZE = 4096  # 读取缓冲区大小
RETRY_DELAY = 0.1  # 重试延迟（秒）

# UI 配置
BACK_BUTTON_WIDTH_RATIO = 0.1  # 返回按钮宽度占比

# 资源路径
DEFAULT_ICON_PATH = "/maixapp/share/icon/ret.png"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def is_in_button(x: int, y: int, btn_pos: Tuple[int, int, int, int]) -> bool:
    return (btn_pos[0] < x < btn_pos[0] + btn_pos[2] and
            btn_pos[1] < y < btn_pos[1] + btn_pos[3])

def get_back_btn_img(width: int) -> Tuple[image.Image, int, int]:
    ret_width = int(width * BACK_BUTTON_WIDTH_RATIO)
    img_back = image.load(DEFAULT_ICON_PATH)
    w, h = (ret_width, img_back.height() * ret_width // img_back.width())
    if w % 2 != 0:
        w += 1
    if h % 2 != 0:
        h += 1
    img_back = img_back.resize(w, h)
    img_back = img_back.rotate(180)
    return img_back, w, h

class HardwareHAL:
    """Hardware Abstraction Layer for thermal camera device management.

    Provides platform-specific serial port configuration and device detection.
    """

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
            raise TypeError(f"Invalid device identifier received: '{dn}'")
        port = cls._PORT_REGISTRY.get(dn)
        if port is None:
            raise RuntimeError(f"Platform mismatch: Device '{dn}' is not supported")
        cls._device = dn
        return port

def main() -> None:
    disp = display.Display()
    disp.set_hmirror(True)
    disp.set_vflip(False)
    ovdisp = disp.add_channel(format=image.Format.FMT_BGRA8888)
    ts = touchscreen.TouchScreen()

    img_back, img_back_w, img_back_h = get_back_btn_img(disp.width())
    back_rect = [0, 0, img_back.width(), img_back.height()]
    ui_img = image.Image(ovdisp.width(), ovdisp.height(), image.Format.FMT_BGRA8888)
    ui_img.draw_image(ovdisp.width()-img_back_w, ovdisp.height()-img_back_h, img_back)
    ovdisp.show(ui_img)

    devices = uart.list_devices()
    if not devices:
        logger.error(
            "Error: No available UART devices found! "
            "Hardware HAL execution aborted."
        )
        return

    hw = HardwareHAL()
    port_name = hw.serial_port()
    serial = uart.UART(port=port_name, baudrate=BAUDRATE_INIT)

    try:
        if HardwareHAL._device == "MaixCAM2":
            serial.write(b'\x44')
            serial.close()
            time.sleep(0.1)
            serial = uart.UART(port=port_name, baudrate=BAUDRATE_HIGH)

        lut = np.array(
            image.cmap_colors_rgb(image.CMap.THERMAL_IRONBOW),
            dtype=np.uint8
        )
        color_buf = np.zeros((PMOD_H, PMOD_W, 3), dtype=np.uint8)
        buffer = bytearray()
        skip = 0
        frame_count = 0

        frame_timestamps = []
        fps_ema = 0.0 

        logger.info(
            "System: Data pump and rendering pipeline successfully initialized."
        )

        ui_reset_needed = False
        capture_start = False
        while not app.need_exit():
            x, y, pressed = ts.read()
            if is_in_button(x, y, back_rect):
                app.set_exit_flag(True)
                break

            chunk = serial.read(UART_BUFFER_SIZE, timeout=SERIAL_TIMEOUT)
            if not chunk and not capture_start:
                ui_reset_needed = True
                main_img = image.Image(disp.width(), disp.height(), image.Format.FMT_RGB888)
                main_img.draw_rect(
                    0, 0, disp.width(), disp.height(), image.COLOR_BLACK, -1
                )
                disp.show(main_img)
                err_img = image.Image(
                    ovdisp.width(), ovdisp.height(), image.Format.FMT_BGRA8888
                )
                err_img.clear()
                msg = "thermal160 device not found"
                char_w = 10 * FONT_SCALE
                char_h = 20 * FONT_SCALE
                x_msg = int((ovdisp.width() - len(msg) * char_w) // 2)
                y_msg = int((ovdisp.height() - char_h) // 2)
                err_img.draw_string(
                    x_msg, y_msg, msg, image.COLOR_WHITE, scale=FONT_SCALE
                )
                err_img = err_img.rotate(180)
                err_img.draw_image(
                    ovdisp.width() - img_back_w,
                    ovdisp.height() - img_back_h,
                    img_back
                )
                ovdisp.show(err_img)
                continue

            if ui_reset_needed:
                ovdisp.show(ui_img)
                ui_reset_needed = False

            if frame_count == 0:
                logger.info("System: First data chunk received.")
            last_data_time = time.time() 
            buffer.extend(chunk)

            while True:
                idx = buffer.find(b'\xFF')
                if idx == -1:
                    buffer.clear()
                    break

                if len(buffer) - (idx + 1) >= FRAME_SIZE:
                    frame_data = buffer[idx + 1 : idx + 1 + FRAME_SIZE]

                    err_idx = frame_data.find(b'\xFF')
                    if err_idx != -1:
                        logger.warning(
                            f"Warning: Protocol violation! Unexpected 0xFF found in "
                            f"payload at offset {err_idx}. Resyncing..."
                        )
                        del buffer[:idx + 1 + err_idx]
                        continue

                    if skip <= SKIP_COUNT:
                        skip += 1
                    else:
                        try:
                            img = image.from_bytes(
                                PMOD_W, PMOD_H, image.Format.FMT_GRAYSCALE, frame_data
                            )
                        except (TypeError, ValueError) as e:
                            img = image.from_bytes(
                                PMOD_W, PMOD_H, image.Format.FMT_GRAYSCALE, bytes(frame_data)
                            )

                        if CMAP:
                            img.gaussian(1)
                            gray_np = image.image2cv(
                                img, ensure_bgr=False, copy=False
                            ).squeeze()
                            np.take(lut, gray_np, axis=0, out=color_buf)
                            img_disp = image.cv2image(color_buf, bgr=False, copy=False)
                        else:
                            img_disp = img
                        capture_start = True
                        disp.show(img_disp)

                        current_time = time.time()
                        frame_timestamps.append(current_time)
                        if len(frame_timestamps) > FPS_WINDOW_SIZE:
                            frame_timestamps.pop(0)
                        if len(frame_timestamps) > 1:
                            window_duration = frame_timestamps[-1] - frame_timestamps[0]
                            if window_duration > 0:
                                window_fps = ((len(frame_timestamps) - 1) / window_duration)
                                if fps_ema == 0.0:
                                    fps_ema = window_fps
                                else:
                                    fps_ema = ((EMA_ALPHA * window_fps) + ((1.0 - EMA_ALPHA) * fps_ema))
                                if frame_count % 10 == 0:
                                        osd_text = f"FPS: {fps_ema:.2f}"
                                        logger.info(osd_text)

                    frame_count += 1
                    buffer = buffer[idx + 1 + FRAME_SIZE:]
                else:
                    if idx > 0:
                        buffer = buffer[idx:]
                    break

    except Exception as e:
        logger.error(f"Fatal: Unhandled pipeline exception: {str(e)}")
        raise
    finally:
        if serial is not None:
            serial.close()
            logger.info("System: UART resource securely released via interrupt vector.")

if __name__ == "__main__":
    main()
