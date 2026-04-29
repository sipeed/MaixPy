import logging
import struct
import time
from typing import Tuple

import numpy as np
import cv2
from maix import app, image, display, touchscreen
from maix.peripheral import uart
from maix.sys import device_name

PMOD_W = 160
PMOD_H = 120
FRAME_PIXEL_SIZE = PMOD_W * PMOD_H
# 物理帧尾 30 字节（与 PC 端 thermocam_gui.exe protocol.py 的 FRAME_SIZE
# = 19231 一致：1 引导 FF + 19200 像素 + 30 telemetry）。本文件只解析前
# 6 字节 (vtemp/t_lo/t_hi)，但 FRAME_SIZE 必须按物理长度算，否则下一帧
# 紧挨校验会落在 NTC 字节上把每帧都误杀。
FRAME_TAIL_SIZE = 30
FRAME_SIZE = FRAME_PIXEL_SIZE + FRAME_TAIL_SIZE
SKIP_COUNT = 10
CMAP = True  # 渲染管线分支路由开关：True为热成像伪彩映射，False为原生灰度零拷贝
INT16_MAX = 0x7FFF

# 配置常量
BAUDRATE_INIT = 2000000
BAUDRATE_HIGH = 4000000
FPS_WINDOW_SIZE = 30
EMA_ALPHA = 0.2
SERIAL_TIMEOUT = 1
FONT_SCALE = 2.0
CENTER_TEMP_SCALE = 1.1
CORNER_TEMP_SCALE = 0.9

# UART 配置
# 单次 read 容量大于一帧（19220 B），让每帧只触发 1 次 serial.read 而非 ~5
# 次，消除多次系统调用的调度开销，是这条流水线最显著的 FPS 瓶颈之一。
UART_BUFFER_SIZE = 32768  # 读取缓冲区大小
RETRY_DELAY = 0.1  # 重试延迟（秒）

# UI 配置
BACK_BUTTON_WIDTH_RATIO = 0.1  # 返回按钮宽度占比

# 资源路径
DEFAULT_ICON_PATH = "/maixapp/share/icon/ret.png"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def pixels_to_temp(pixels: np.ndarray, t_lo: float, t_hi: float) -> np.ndarray:
    if t_hi <= t_lo:
        return np.full_like(pixels, t_lo, dtype=np.float32)
    norm = (pixels.astype(np.float32) / 254.0).clip(0.0, 1.0)
    return (t_lo + (t_hi - t_lo) * norm).astype(np.float32)


def draw_cross(img_disp: image.Image, x: int, y: int, color, size: int = 12) -> None:
    img_disp.draw_line(x - size, y, x + size, y, color)
    img_disp.draw_line(x, y - size, x, y + size, color)


def draw_label(img_disp: image.Image, x: int, y: int, text: str, color, scale: float = 0.8) -> None:
    img_disp.draw_string(x + 1, y + 1, text, image.COLOR_BLACK, scale=scale)
    img_disp.draw_string(x, y, text, color, scale=scale)


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
    img_back = img_back.rotate(0)
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
    disp.set_hmirror(False)
    disp.set_vflip(True)
    ts = touchscreen.TouchScreen()

    img_back, img_back_w, img_back_h = get_back_btn_img(disp.width())
    back_rect = [0, 0, img_back_w, img_back_h]

    img_cmap: image.Image = None
    cmap_rect = [
        disp.width() - int(disp.width() * BACK_BUTTON_WIDTH_RATIO),
        disp.height() - 0,
        1,
        1,
    ]

    def init_cmap_btn(label: str) -> None:
        nonlocal img_cmap, cmap_rect
        w, h = img_back_w, img_back_h
        img_cmap = image.Image(w, h, image.Format.FMT_RGB888)
        img_cmap.draw_rect(0, 0, w, h, image.COLOR_BLACK, -1)
        char_h = 15
        text_y = (h - char_h) // 2
        text_x = max(2, (w - len(label) * 6) // 2)
        img_cmap.draw_string(text_x, text_y, label, image.COLOR_WHITE, scale=0.6)
        img_cmap = img_cmap.rotate(0)
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
            serial.write(b"\x44")
            serial.close()
            time.sleep(0.1)
            serial = uart.UART(port=port_name, baudrate=BAUDRATE_HIGH)

        def _safe_colormap(name: str, fallback_id: int):
            cp = getattr(cv2, name, fallback_id)
            test = np.arange(256, dtype=np.uint8).reshape(1, 256)
            try:
                cv2.applyColorMap(test, cp)
                return (name.replace("COLORMAP_", "").lower(), cp)
            except Exception:
                return None

        # TURBO 放首位作为默认：中段为绿/黄，均匀场景噪声映射过去是自然
        # 过渡色，从根本上消除 HOT 默认下的「静置偏红」。HOT/COOL 等仍在列
        # 表里，CMAP 按键可循环切换，用户需要 HOT 风格随时可切回。
        cmap_options = []
        for _name, _fid in [
            ("COLORMAP_TURBO", 20),
            ("COLORMAP_HOT", 0),
            ("COLORMAP_COOL", 1),
            ("COLORMAP_DEEPGREEN", 15),
            ("COLORMAP_MAGMA", 13),
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

        disp_w, disp_h = disp.width(), disp.height()
        # 双缓冲：两个物理缓冲轮替。当前帧写 buffer[i]，disp.show 异步读取
        # 的同时下一帧写 buffer[i^1]，不会与 DMA 读竞争。配合下面的
        # copy=False，省掉 cv2image 每帧~900KB 的内存拷贝。
        disp_buffers = [
            np.zeros((disp_h, disp_w, 3), dtype=np.uint8),
            np.zeros((disp_h, disp_w, 3), dtype=np.uint8),
        ]
        db_idx = 0

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
                time.sleep(0.2)

            chunk = serial.read(UART_BUFFER_SIZE, SERIAL_TIMEOUT)
            if chunk:
                chunk = bytes(chunk)

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
                main_img.draw_image(0, 0, img_back)
                if img_cmap is not None:
                    main_img.draw_image(disp_w - img_back_w, disp_h - img_back_h, img_cmap)
                disp.show(main_img)
                continue
            if frame_count == 0:
                logger.info("System: First data chunk received.")
            buffer.extend(chunk)

            # ---- Drain-to-latest 同步策略 ----
            # 同 PC 端 thermocam_gui.exe 的等价行为：解析阶段把缓冲里所有合
            # 法帧全部消费掉，但只保留 *最后一帧* 用于渲染，丢弃中间帧。
            # 单线程下 disp.show + cv2 流水线一旦落后，串口侧会堆积多帧；
            # 旧版"每解析一帧就渲染一帧"会把延迟越拉越大，缓冲越拉越长，
            # 既导致屏幕卡顿、也提高了伪 0xFF 假同步的命中率（就是 output/
            # 里那张半幅错乱图的成因）。drain-to-latest 让每外循环最多一
            # 次重渲染，CPU 富余、缓冲不堆积、误同步概率断崖下降。
            latest_frame_data = None
            latest_t_lo_x10 = INT16_MAX
            latest_t_hi_x10 = INT16_MAX
            while True:
                idx = buffer.find(b"\xFF")
                if idx == -1:
                    buffer.clear()
                    break
                if len(buffer) - (idx + 1) < FRAME_SIZE:
                    if idx > 0:
                        del buffer[:idx]
                    break

                frame_data = bytes(buffer[idx + 1: idx + 1 + FRAME_SIZE])

                # 帧对齐校验走 telemetry 合理性，而非"像素区内有 0xFF 就
                # 重同步"——后者会把固件 FFC 瞬态/饱和像素产生的合法 255
                # 也误判为失步。VTEMP 是 14-bit 大端（固件对每行累加前已
                # &0x3FFF），telemetry[0] 高 2 bit 恒为 0；t_lo/t_hi 是
                # °C×10 的物理量，落在合理区间且 t_hi≥t_lo。
                telemetry = frame_data[FRAME_PIXEL_SIZE:]
                if telemetry[0] & 0xC0:
                    del buffer[:idx + 1]
                    continue
                t_lo_x10 = struct.unpack_from(">h", telemetry, 2)[0]
                t_hi_x10 = struct.unpack_from(">h", telemetry, 4)[0]
                if t_lo_x10 != INT16_MAX and t_hi_x10 != INT16_MAX:
                    if not (-1000 <= t_lo_x10 <= 3200 and
                            -1000 <= t_hi_x10 <= 3200 and
                            t_hi_x10 >= t_lo_x10):
                        del buffer[:idx + 1]
                        continue

                # 帧间紧挨校验：协议里相邻两帧背靠背，下一帧的 0xFF 必须正
                # 好出现在本帧消费完的位置。这条 magic 能筛掉"FF + telemetry
                # 凑巧合理 + 像素区中段被 UART RX FIFO 短暂溢出/固件脏数据
                # 污染"的坏帧——这种坏帧在 drain-to-latest 下会持续显示一
                # 整个 drain 周期，比单帧渲染时显眼得多（即 output/ 里上 1/3
                # 真实图像 + 下 2/3 椒盐噪声那张图的成因）。
                # 缓冲不够长时跳过此校验，留到下一轮 drain 再判。
                next_ff_pos = idx + 1 + FRAME_SIZE
                if len(buffer) > next_ff_pos and buffer[next_ff_pos] != 0xFF:
                    del buffer[:idx + 1]
                    continue

                # 通过校验，推进缓冲并记账
                del buffer[:idx + 1 + FRAME_SIZE]
                frame_count += 1

                if skip <= SKIP_COUNT:
                    skip += 1
                    continue

                # 关键：只保留缓冲里最后一帧用于渲染，旧帧直接丢弃
                latest_frame_data = frame_data
                latest_t_lo_x10 = t_lo_x10
                latest_t_hi_x10 = t_hi_x10

            if latest_frame_data is None:
                continue

            # ===== 渲染最新一帧（每外循环最多一次 disp.show）=====
            t_lo_x10 = latest_t_lo_x10
            t_hi_x10 = latest_t_hi_x10
            gray_np = np.frombuffer(latest_frame_data[:FRAME_PIXEL_SIZE], dtype=np.uint8).reshape(PMOD_H, PMOD_W)
            gray_np = cv2.flip(gray_np, -1)
            has_temp = (
                t_lo_x10 != INT16_MAX and
                t_hi_x10 != INT16_MAX and
                t_hi_x10 > t_lo_x10
            )

            # 选中当前帧要写入的物理缓冲。另一个缓冲此刻可能仍被
            # 上一帧的 disp.show DMA 读取，不会被本帧写动。
            disp_buffer = disp_buffers[db_idx]
            if CMAP:
                gray_blurred = cv2.GaussianBlur(gray_np, (3, 3), 1)
                np.take(lut, gray_blurred, axis=0, out=color_buf)
                cv2.resize(color_buf, (disp_w, disp_h), dst=disp_buffer, interpolation=cv2.INTER_LINEAR)
            else:
                gray_resized = cv2.resize(gray_np, (disp_w, disp_h), interpolation=cv2.INTER_LINEAR)
                disp_buffer[:, :, 0] = gray_resized
                disp_buffer[:, :, 1] = gray_resized
                disp_buffer[:, :, 2] = gray_resized

            # 双缓冲保护下安全启用 copy=False，省掉每帧 ~900KB 的
            # cv2image 内部 memcpy。竞态由缓冲轮替天然隔离。
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
                    f"{center_temp:.1f}C",
                    image.COLOR_WHITE,
                    scale=CENTER_TEMP_SCALE,
                )

                text_x = 8
                text_y = disp_h - 82
                draw_label(
                    img_disp,
                    text_x,
                    text_y,
                    f"MAX {temp_img[max_y, max_x]:.1f}C",
                    image.COLOR_RED,
                    scale=CORNER_TEMP_SCALE,
                )
                draw_label(
                    img_disp,
                    text_x,
                    text_y + 26,
                    f"MIN {temp_img[min_y, min_x]:.1f}C",
                    image.COLOR_BLUE,
                    scale=CORNER_TEMP_SCALE,
                )
                draw_label(
                    img_disp,
                    text_x,
                    text_y + 52,
                    f"RNG {t_lo:.1f}~{t_hi:.1f}C",
                    image.COLOR_WHITE,
                    scale=0.85,
                )

            img_disp.draw_image(0, 0, img_back)
            if img_cmap is not None:
                img_disp.draw_image(disp_w - img_back_w, disp_h - img_back_h, img_cmap)

            capture_start = True
            disp.show(img_disp)
            db_idx ^= 1  # 切到另一个物理缓冲供下一帧写入

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

    except Exception as e:
        logger.error(f"Fatal: Unhandled pipeline exception: {str(e)}")
        raise
    finally:
        if serial is not None:
            serial.close()
            logger.info("System: UART resource securely released via interrupt vector.")


if __name__ == "__main__":
    main()
