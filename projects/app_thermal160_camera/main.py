import logging
import time
from typing import Tuple

import numpy as np
import cv2
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
    ts = touchscreen.TouchScreen()

    img_back, img_back_w, img_back_h = get_back_btn_img(disp.width())
    back_rect = [0, 0, img_back_w, img_back_h]

    # CMAP 按钮（动态更新，延迟初始化）
    img_cmap: image.Image = None
    cmap_rect = [
        disp.width() - int(disp.width() * BACK_BUTTON_WIDTH_RATIO),
        disp.height() - 0,
        1,
        1,
    ]  # 占位，后续用 init_cmap_btn 填充

    def init_cmap_btn(label: str) -> None:
        nonlocal img_cmap, cmap_rect
        w, h = img_back_w, img_back_h
        img_cmap = image.Image(w, h, image.Format.FMT_RGB888)
        img_cmap.draw_rect(0, 0, w, h, image.COLOR_BLACK, -1)
        char_h = 15
        text_y = (h - char_h) // 2
        text_x = max(2, (w - len(label) * 6) // 2)
        img_cmap.draw_string(text_x, text_y, label, image.COLOR_WHITE, scale=0.6)
        img_cmap = img_cmap.rotate(180)
        cmap_rect = [disp.width() - w, disp.height() - h, w, h]

    init_cmap_btn("CMAP")

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

        def _safe_colormap(name: str, fallback_id: int):
            """安全获取 colormap ID，不支持时返回 None。"""
            cp = getattr(cv2, name, fallback_id)
            test = np.arange(256, dtype=np.uint8).reshape(1, 256)
            try:
                cv2.applyColorMap(test, cp)
                return (name.replace("COLORMAP_", "").lower(), cp)
            except Exception:
                return None

        cmap_options = []
        for _name, _fid in [
            ("COLORMAP_HOT", 0),
            ("COLORMAP_COOL", 1),
            ("COLORMAP_DEEPGREEN", 15),
            ("COLORMAP_MAGMA", 13),
            ("COLORMAP_TURBO", 20),
        ]:
            entry = _safe_colormap(_name, _fid)
            if entry:
                cmap_options.append(entry)

        if not cmap_options:
            logger.error("Error: No supported colormaps available.")
            return

        cmap_idx = 0

        def get_cv2_lut(idx):
            _, cp = cmap_options[idx]
            gray = np.arange(256, dtype=np.uint8).reshape(1, 256)
            colored = cv2.applyColorMap(gray, cp)
            return cv2.cvtColor(colored, cv2.COLOR_BGR2RGB).reshape(256, 3)

        cmap_abbrev = {"hot": "HOT", "cool": "COOL", "deepgreen": "DGRN", "magma": "MAGM", "turbo": "TRBO"}

        def redraw_cmap_btn() -> None:
            name = cmap_options[cmap_idx][0]
            label = cmap_abbrev.get(name, name[:5].upper())
            init_cmap_btn(label)

        lut = get_cv2_lut(cmap_idx)
        color_buf = np.zeros((PMOD_H, PMOD_W, 3), dtype=np.uint8)

        # 预分配显示缓冲区，避免循环内频繁创建对象导致撕裂
        disp_w, disp_h = disp.width(), disp.height()
        disp_buffer = np.zeros((disp_h, disp_w, 3), dtype=np.uint8)

        buffer = bytearray()
        skip = 0
        frame_count = 0

        frame_timestamps = []
        fps_ema = 0.0 

        logger.info(
            "System: Data pump and rendering pipeline successfully initialized."
        )

        capture_start = False
        while not app.need_exit():
            x, y, pressed = ts.read()
            if is_in_button(x, y, back_rect):
                app.set_exit_flag(True)
                break

            if pressed and is_in_button(x, y, cmap_rect):
                cmap_idx = (cmap_idx + 1) % len(cmap_options)
                lut = get_cv2_lut(cmap_idx)
                redraw_cmap_btn()
                logger.info(f"System: Switched to colormap {cmap_options[cmap_idx][0]}")
                time.sleep(0.2)  # 防抖

            chunk = serial.read(UART_BUFFER_SIZE, timeout=SERIAL_TIMEOUT)
            if not chunk and not capture_start:
                main_img = image.Image(disp.width(), disp.height(), image.Format.FMT_RGB888)
                main_img.draw_rect(
                    0, 0, disp.width(), disp.height(), image.COLOR_BLACK, -1
                )
                msg = "thermal160 device not found"
                char_w = 10 * FONT_SCALE
                char_h = 20 * FONT_SCALE
                x_msg = int((disp.width() - len(msg) * char_w) // 2)
                y_msg = int((disp.height() - char_h) // 2)
                main_img.draw_string(
                    x_msg, y_msg, msg, image.COLOR_WHITE, scale=FONT_SCALE
                )
                # 方向：统一旋转 180 度，并绘制按钮
                main_img = main_img.rotate(180)
                main_img.draw_image(disp.width() - img_back_w, disp.height() - img_back_h, img_back)
                if img_cmap is not None:
                    main_img.draw_image(0, 0, img_cmap)
                disp.show(main_img)
                continue

            if frame_count == 0:
                logger.info("System: First data chunk received.")
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
                        # 直接将帧数据转为 numpy 数组，避免创建 Image 对象
                        gray_np = np.frombuffer(frame_data, dtype=np.uint8).reshape(PMOD_H, PMOD_W)

                        if CMAP:
                            # 高斯模糊（使用 OpenCV 加速）
                            gray_blurred = cv2.GaussianBlur(gray_np, (3, 3), 1)
                            # 颜色映射到预分配缓冲区
                            np.take(lut, gray_blurred, axis=0, out=color_buf)
                            # 直接缩放到显示缓冲区，避免中间对象创建
                            cv2.resize(color_buf, (disp_w, disp_h), dst=disp_buffer, interpolation=cv2.INTER_LINEAR)
                        else:
                            # 灰度图：先缩放单通道，然后复制到三通道
                            gray_resized = cv2.resize(gray_np, (disp_w, disp_h), interpolation=cv2.INTER_LINEAR)
                            disp_buffer[:,:,0] = gray_resized
                            disp_buffer[:,:,1] = gray_resized
                            disp_buffer[:,:,2] = gray_resized
                        
                        # 创建显示图像
                        img_disp = image.cv2image(disp_buffer, bgr=False, copy=False)
                        img_disp.draw_image(disp_w - img_back_w, disp_h - img_back_h, img_back)
                        if img_cmap is not None:
                            img_disp.draw_image(0, 0, img_cmap)
                        
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
