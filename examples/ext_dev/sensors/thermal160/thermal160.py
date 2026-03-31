import numpy as np
import time
from maix import app, image, display
from maix.peripheral import uart
from maix.sys import device_name

PMOD_W = 160
PMOD_H = 120
FRAME_SIZE = PMOD_W * PMOD_H
SKIP_COUNT = 10

CMAP = True  # 渲染管线分支路由开关：True为热成像伪彩映射，False为原生灰度零拷贝

class HardwareHAL:
    _PORT_REGISTRY = {
        "MaixCAM2": "/dev/ttyS2",
        # 以下设备将在后续逐步提供支持
        "MaixCAM": None,
        "MaixCAM-Pro": None,
    }
    _device = ""

    @classmethod
    def serial_port(cls):
        dn = device_name()
        if not isinstance(dn, str) or not dn.strip():
            raise TypeError(f"Invalid device identifier received: '{dn}'")
        port = cls._PORT_REGISTRY.get(dn)
        if port is None:
            raise RuntimeError(f"Platform mismatch: Device '{dn}' is not supported")
        cls._device = dn
        return port

def main():
    disp = display.Display()
    disp.set_hmirror(True)
    disp.set_vflip(False)

    devices = uart.list_devices()
    if not devices:
        print("Error: No available UART devices found! Hardware HAL execution aborted.")
        return

    hw = HardwareHAL()
    port_name = hw.serial_port()
    serial = uart.UART(port=port_name, baudrate=2000000)

    try:
        if HardwareHAL._device == "MaixCAM2":
            serial.write(b'\x44')
            serial.close()
            time.sleep(0.1)
            serial = uart.UART(port=port_name, baudrate=4000000)

        lut = np.array(image.cmap_colors_rgb(image.CMap.THERMAL_IRONBOW), dtype=np.uint8)
        color_buf = np.zeros((PMOD_H, PMOD_W, 3), dtype=np.uint8)
        buffer = bytearray()
        skip = 0
        frame_count = 0

        fps_window_size = 30 
        frame_timestamps = []
        fps_ema = 0.0
        ema_alpha = 0.2 

        print("System: Data pump and rendering pipeline successfully initialized.")

        while not app.need_exit():
            chunk = serial.read(4096, timeout=10)
            if not chunk:
                continue
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
                        print(f"Warning: Protocol violation! Unexpected 0xFF found in payload at offset {err_idx}. Resyncing...")
                        del buffer[:idx + 1 + err_idx]
                        continue

                    if skip <= SKIP_COUNT:
                        skip += 1
                    else:
                        try:
                            img = image.from_bytes(PMOD_W, PMOD_H, image.Format.FMT_GRAYSCALE, frame_data)
                        except TypeError:
                            img = image.from_bytes(PMOD_W, PMOD_H, image.Format.FMT_GRAYSCALE, bytes(frame_data))

                        if CMAP:
                            img.gaussian(1)
                            gray_np = image.image2cv(img, ensure_bgr=False, copy=False).squeeze()
                            np.take(lut, gray_np, axis=0, out=color_buf)
                            img_disp = image.cv2image(color_buf, bgr=False, copy=False)
                        else:
                            img_disp = img
                        disp.show(img_disp)

                        current_time = time.time()
                        frame_timestamps.append(current_time)
                        if len(frame_timestamps) > fps_window_size:
                            frame_timestamps.pop(0)
                        if len(frame_timestamps) > 1:
                            window_duration = frame_timestamps[-1] - frame_timestamps[0]
                            if window_duration > 0:
                                window_fps = (len(frame_timestamps) - 1) / window_duration
                                if fps_ema == 0.0:
                                    fps_ema = window_fps
                                else:
                                    fps_ema = (ema_alpha * window_fps) + ((1.0 - ema_alpha) * fps_ema)
                                if frame_count % 10 == 0:
                                    osd_text = f"FPS: {fps_ema:.2f}"
                                    print(osd_text)

                    frame_count += 1
                    buffer = buffer[idx + 1 + FRAME_SIZE:]
                else:
                    if idx > 0:
                        buffer = buffer[idx:]
                    break

    except Exception as e:
        print(f"Fatal: Unhandled pipeline exception: {str(e)}")
        raise
    finally:
        if 'serial' in locals() and serial:
            serial.close()
            print("System: UART resource securely released via interrupt vector.")

if __name__ == "__main__":
    main()
