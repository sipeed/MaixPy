from maix import pinmap
from maix import i2c, spi
from maix import time, app, sys
from maix import display, app, image, nn, tensor, touchscreen, camera
import numpy as np
import cv2
import inspect
import os
import json

if sys.device_name().lower() != "maixcam2":
    raise Exception("This project only support MaixCAM2")

# --- 0. 耗时打印 ---
DBG_T = False
def dbg_time(name, t):
    if DBG_T:
        print("%s %d ms"%(name, t))

# --- 1. 系统配置 ---
ts = touchscreen.TouchScreen()
disp = display.Display()
print(f"display size: {disp.width()}x{disp.height()}")
old_ai_isp = int(app.get_sys_config_kv("npu", "ai_isp", "0"))
app.set_sys_config_kv("npu", "ai_isp", "1")

# --- 2. 摄像头初始化 ---
print("Init Camera...")
cam = None
try:
    cam = camera.Camera(disp.width(), disp.height())
    print("Camera Init Success")
except Exception as e:
    print(f"Camera Init Failed: {e}")

image.load_font("sourcehansans", "/maixapp/share/font/SourceHanSansCN-Regular.otf", size = 20)

img = image.Image(320, 240)
img.clear()
img.draw_string(10, 100, "Initializing (Wait 8s)...\nNote:Open AI-ISP option first", image.COLOR_WHITE, font="sourcehansans")
disp.show(img)

# --- 全局变量 ---
PREVIEW_TEMP = True
enable_x3 = True
EDGE_TEMP_THRESHOLD = 5.0

# --- 3. 硬件引脚配置 ---
pin_function = {
    "A8": "I2C7_SCL", "A9": "I2C7_SDA",
    "B21": "SPI2_CS1", "B19": "SPI2_MISO", "B18": "SPI2_MOSI", "B20": "SPI2_SCK"
}
for pin, func in pin_function.items():
    if 0 != pinmap.set_pin_function(pin, func):
        print(f"Failed: pin{pin}, func{func}")

# --- 4. 驱动初始化 ---
bus = i2c.I2C(7, i2c.Mode.MASTER)
spidev = spi.SPI(2, spi.Mode.MASTER, 30000000, 1, 1, hw_cs=1)

BUFF_LEN = 4096
DUMMY_LEN = 512

def SPIDataRW(spi_id, tx_data: bytearray, rx_data: bytearray, length: int):
    to_send = bytes(tx_data[:length])
    result = spidev.write_read(to_send, length)
    rx_data[:length] = result

def spi_frame_get(raw_frame: bytearray, frame_byte_size: int, frame_type: int) -> int:
    tx_Data = bytearray(BUFF_LEN)
    rx_Data = bytearray(BUFF_LEN)
    i = 0
    new_frame_cmd = 0 if frame_type == 0 else 0xCC
    continue_cmd = 0x55

    tx_Data[0] = new_frame_cmd if frame_type != 0 else 0xAA
    SPIDataRW(0, tx_Data, rx_Data, BUFF_LEN)
    raw_frame[i:i + BUFF_LEN - DUMMY_LEN] = rx_Data[DUMMY_LEN:BUFF_LEN]
    i += BUFF_LEN - DUMMY_LEN
    if rx_Data[480] != 1: return -1

    while frame_byte_size - i > BUFF_LEN:
        tx_Data[0] = continue_cmd
        SPIDataRW(0, tx_Data, rx_Data, BUFF_LEN)
        raw_frame[i:i + BUFF_LEN] = rx_Data[:BUFF_LEN]
        i += BUFF_LEN

    tx_Data[0] = continue_cmd
    SPIDataRW(0, tx_Data, rx_Data, BUFF_LEN)
    raw_frame[i:i + (frame_byte_size - i)] = rx_Data[:frame_byte_size - i]
    SPIDataRW(0, tx_Data, rx_Data, BUFF_LEN)
    return 0

# --- 5. 热成像初始化 ---
wh = [0x1d, 0x00]
print("VCMD_PREVIEW_STOP")
bus.writeto(0x3c, bytes(wh+[0x0f, 0x02, 0x00, 0x00, 0x00, 0x00, 0x08, 0x00]))
time.sleep(1)

print("VCMD_PREVIEW_START")
width, height = 256, 192
bus.writeto(0x3c, bytes(wh+[0x0f, 0xc1, 0x00, 0x00, 0x00, 0x00, 0x08, 0x00, 0, 0, width>>8, width&0xff, height>>8, height&0xff, 25, 8]))
time.sleep(5)

print("VCMD_TEMP_PREVIEW_START")
bus.writeto(0x3c, bytes(wh+[0x0a, 0x01 if PREVIEW_TEMP else 0x02, 0, 0x00, 0x00, 0x00, 0x00, 0x00]))
time.sleep(2)

if not PREVIEW_TEMP:
    print("pseudo_color_set")
    bus.writeto(0x3c, bytes(wh+[0x09, 0xc4, 0, 0x00, 0x00, 0x00, 0x00, 0x01, 0x01]))
    time.sleep(1)

# --- 6. 图像算法函数 ---

def align_camera_image(vis_np, target_w, target_h, scale, off_x, off_y):
    t0_align = time.ticks_ms()
    h_src, w_src = vis_np.shape[:2]

    src_w_need = target_w / scale
    src_h_need = target_h / scale
    cx_src = w_src / 2
    cy_src = h_src / 2

    src_x = cx_src - (src_w_need / 2) - (off_x / scale)
    src_y = cy_src - (src_h_need / 2) - (off_y / scale)

    x0 = int(src_x); y0 = int(src_y)
    w0 = int(src_w_need); h0 = int(src_h_need)

    x1 = max(0, x0); y1 = max(0, y0)
    x2 = min(w_src, x0 + w0); y2 = min(h_src, y0 + h0)

    vis_aligned = None

    if x2 > x1 and y2 > y1:
        crop = vis_np[y1:y2, x1:x2]
        if x1 == x0 and y1 == y0 and x2 == (x0+w0) and y2 == (y0+h0):
            vis_aligned = cv2.resize(crop, (target_w, target_h), interpolation=cv2.INTER_NEAREST)
        else:
            dst_w = int((x2 - x1) * scale)
            dst_h = int((y2 - y1) * scale)
            if dst_w > 0 and dst_h > 0:
                crop_resized = cv2.resize(crop, (dst_w, dst_h), interpolation=cv2.INTER_NEAREST)
                vis_aligned = np.zeros((target_h, target_w, 3), dtype=np.uint8)
                dx = int((x1 - src_x) * scale)
                dy = int((y1 - src_y) * scale)
                h_paste, w_paste = crop_resized.shape[:2]
                dy2 = min(target_h, dy + h_paste)
                dx2 = min(target_w, dx + w_paste)
                if dy2 > dy and dx2 > dx:
                    vis_aligned[dy:dy2, dx:dx2] = crop_resized[:(dy2-dy), :(dx2-dx)]

    if vis_aligned is None:
        vis_aligned = np.zeros((target_h, target_w, 3), dtype=np.uint8)

    t1_align = time.ticks_ms()
    dbg_time("cam fast_align", t1_align - t0_align)
    return vis_aligned

def scale_to_range(arr, target_min, target_max):
    return cv2.normalize(arr, None, float(target_min), float(target_max), cv2.NORM_MINMAX, cv2.CV_8U)

def process_edge_fusion(vis_img, thermal_gray_img, t_min, t_max):
    diff_temp = (t_max - t_min) / 64.0
    if diff_temp < EDGE_TEMP_THRESHOLD:
        return vis_img

    blur = thermal_gray_img
    edges = cv2.Canny(blur, 50,150)
    kernel = np.ones((3, 3), np.uint8)
    edges_thick = cv2.dilate(edges, kernel, iterations=1)
    edges_soft = cv2.GaussianBlur(edges_thick, (3, 3), 0)

    edge_b = np.zeros_like(edges_soft)
    edge_g = (edges_soft * 0.84).astype(np.uint8)
    edge_r = edges_soft
    colored_edges = cv2.merge([edge_b, edge_g, edge_r])

    fused = cv2.add(vis_img, colored_edges)
    return fused

# 全局预计算 LUT (平方曲线)
def create_alpha_lut():
    lut = np.zeros(256, dtype=np.uint8)
    sensitivity = 80.0
    min_opacity = 0.10
    max_opacity = 0.90
    for i in range(256):
        factor = min(i / sensitivity, 1.0)
        factor = factor * factor
        alpha = min_opacity + factor * (max_opacity - min_opacity)
        lut[i] = int(alpha * 255)
    return lut

ALPHA_LUT = create_alpha_lut()

# 【还原】使用您提供的 float32 版本，保证画质正确
def process_adaptive_mix(vis_img, thermal_gray, thermal_color, temp_diff):
    """
    查表法自适应融合 (Float32 Vectorized)
    """
    if temp_diff < EDGE_TEMP_THRESHOLD:
        return cv2.addWeighted(vis_img, 0.6, thermal_color, 0.4, 0)

    small = cv2.resize(thermal_gray, (64, 48), interpolation=cv2.INTER_NEAREST)
    median_val = int(np.median(small))
    
    diff = cv2.absdiff(thermal_gray, median_val)
    alpha_map = cv2.LUT(diff, ALPHA_LUT)
    alpha_3c = cv2.merge([alpha_map, alpha_map, alpha_map])
    
    # 浮点混合运算 (避免溢出且支持逐像素权重)
    alpha_f = alpha_3c.astype(np.float32) * (1.0/255.0)
    vis_f = vis_img.astype(np.float32)
    therm_f = thermal_color.astype(np.float32)
    
    fused = vis_f + alpha_f * (therm_f - vis_f)
    
    return fused.astype(np.uint8)

# --- 7. 配置管理 ---
CONFIG_FILE = "/root/fusion.json"

CMAP_LIST = [
    ("Hot", cv2.COLORMAP_HOT),
    ("Cool", cv2.COLORMAP_COOL),
    ("Magma", cv2.COLORMAP_MAGMA),
    ("Turbo", cv2.COLORMAP_TURBO),
    ("Night", cv2.COLORMAP_DEEPGREEN),
]

def load_config():
    default_config = {
        'scale': 1.0, 'x': 0, 'y': 0,
        'cmap_idx': 0,
        'sr_therm': True,
        'sr_mix': False,
        'sr_edge': True
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f: return json.load(f)
        except: return default_config
    return default_config

def save_config(state):
    config = {
        'scale': state['scale'], 'x': state['x'], 'y': state['y'],
        'cmap_idx': state['cmap_idx'],
        'sr_therm': state['sr_therm'],
        'sr_mix': state['sr_mix'],
        'sr_edge': state['sr_edge']
    }
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
            os.fsync(f.fileno())
    except: pass

# --- UI 逻辑 ---
MODES = ["Vis", "Therm", "Mix", "Edge"]

def draw_ui(img, w, h, state, temp_diff):
    if state['hide_hud']:
        img.draw_circle(15, h-15, 4, image.COLOR_GREEN, thickness=4)
        return

    mode_str = f"Mode: {MODES[state['mode']]}"
    img.draw_string(5, 5, mode_str, image.COLOR_YELLOW, scale=2.5)

    # 【修改】SR 开关在 Mode 1 和 Mode 2 均显示
    if state['mode'] in [1, 2]:
        # 获取当前模式对应的 SR 状态
        is_sr_on = state['sr_therm'] if state['mode'] == 1 else state['sr_mix']
        sr_color = image.COLOR_GREEN if is_sr_on else image.COLOR_RED
        img.draw_string(5, h//2 - 20, "SR", sr_color, scale=2.5)

    if state['mode'] in [1, 2]:
        cmap_name = CMAP_LIST[state['cmap_idx']][0]
        img.draw_string(w-110, h//2 - 20, cmap_name, image.COLOR_YELLOW, scale=2.5)

    if state['mode'] in [2, 3]:
        color = image.COLOR_GREEN if temp_diff >= EDGE_TEMP_THRESHOLD else image.COLOR_RED
        img.draw_string(5, 40, f"d:{temp_diff:.1f}", color, scale=1.5)

    if state['mode'] != 1:
        img.draw_string(w-160, 5, f"Sc:{state['scale']:.2f}", image.COLOR_WHITE, scale=2.5)
        img.draw_string(w-160, 60, "[-]", image.COLOR_GREEN, scale=3.0)
        img.draw_string(w-80,  60, "[+]", image.COLOR_RED,   scale=3.0)
        img.draw_string(w-190, h-125, f"X:{state['x']} Y:{state['y']}", image.COLOR_WHITE, scale=2.0)
        img.draw_string(w-85, h-110, "^", image.COLOR_WHITE, scale=3.0)
        img.draw_string(w-85, h-45,  "v", image.COLOR_WHITE, scale=2.5)
        img.draw_string(w-130, h-75, "<", image.COLOR_WHITE, scale=3.0)
        img.draw_string(w-40,  h-75, ">", image.COLOR_WHITE, scale=3.0)

    img.draw_string(5, h-50, "Hide", image.COLOR_BLUE, scale=2.5)

def process_touch(ts, w, h, state):
    x, y, pressed = ts.read()
    if not pressed:
        state['hud_lock'] = False
        state['mode_lock'] = False
        state['sr_lock'] = False
        state['cmap_lock'] = False
        return

    if x >= 0 and x <= 150 and y >= 0 and y <= 80:
        if not state['mode_lock']:
            state['mode'] = (state['mode'] + 1) % 4
            state['mode_lock'] = True

    if x >= 0 and x <= 120 and y >= h - 80:
        if not state['hud_lock']:
            state['hide_hud'] = not state['hide_hud']
            state['hud_lock'] = True

    if state['hide_hud']: return

    # 3. SR 开关 - 支持 Mode 1 和 Mode 2
    if state['mode'] in [1, 2]:
        if x >= 0 and x <= 100 and y >= h//2 - 40 and y <= h//2 + 40:
            if not state['sr_lock']:
                if state['mode'] == 1:
                    state['sr_therm'] = not state['sr_therm']
                elif state['mode'] == 2:
                    state['sr_mix'] = not state['sr_mix']
                state['sr_lock'] = True

    if state['mode'] in [1, 2]:
        if x >= w - 120 and y >= h//2 - 40 and y <= h//2 + 40:
            if not state['cmap_lock']:
                state['cmap_idx'] = (state['cmap_idx'] + 1) % len(CMAP_LIST)
                state['cmap_lock'] = True

    if state['mode'] == 1: return

    if y >= 50 and y <= 130 and x > 150:
        if x >= w - 180 and x < w - 80:   state['scale'] = max(0.1, state['scale'] - 0.05)
        elif x >= w - 80 and x <= w:      state['scale'] += 0.05

    if x >= w - 160 and y >= h - 160:
        dx, dy = x - (w - 70), y - (h - 70)
        if abs(dx) > 15 or abs(dy) > 15:
            if abs(dx) > abs(dy): state['x'] += 2 if dx > 0 else -2
            else:                 state['y'] += 2 if dy > 0 else -2


# --- 8. 主程序 ---
cfg = load_config()
state = {
    'scale': cfg.get('scale', 1.0),
    'x': int(cfg.get('x', 0)),
    'y': int(cfg.get('y', 0)),
    'cmap_idx': cfg.get('cmap_idx', 0),
    'sr_therm': cfg.get('sr_therm', True),
    'sr_mix': cfg.get('sr_mix', False),
    'sr_edge': cfg.get('sr_edge', True),
    'hide_hud': False,
    'hud_lock': False,
    'mode': 1,
    'mode_lock': False,
    'sr_lock': False,
    'cmap_lock': False
}
print(f"State: {state}")

x3model_name = '/root/models/sr2.5_ir32_npu1.mud'
print(f"Loading Model: {x3model_name}")
x3model = nn.NN(x3model_name)
output_layer_name = 'output'
image_frame = bytearray(width*height*2)

print("Start Loop...")
last_frame_ms = time.ticks_ms()
current_temp_diff = 0.0

while not app.need_exit():
    t0 = time.ticks_ms()
    mode = state['mode']
    # Mode 0: Vis
    if mode == 0:
        cam_img = None
        if cam:
            try: cam_img = cam.read()
            except: pass
        t1=time.ticks_ms();dbg_time("cam cap", t1-t0);t0=t1

        if cam_img is not None:
            vis_np = image.image2cv(cam_img, ensure_bgr=True)
            t1=time.ticks_ms();dbg_time("cam2cv", t1-t0);t0=t1

            final_img_np = align_camera_image(vis_np, disp.width(), disp.height(), state['scale'], state['x'], state['y'])
            # cam fast_align inside
        else:
            final_img_np = np.zeros((disp.height(), disp.width(), 3), dtype=np.uint8)

        img = image.cv2image(final_img_np)
        t1=time.ticks_ms();dbg_time("cv2image", t1-t0);t0=t1

        draw_ui(img, disp.width(), disp.height(), state, current_temp_diff)
        t1=time.ticks_ms();dbg_time("ui", t1-t0);t0=t1
        disp.show(img)
        t1=time.ticks_ms();dbg_time("show", t1-t0);t0=t1

        now = time.ticks_ms()
        # 帧率计算修正为 (last, now)
        print(f"==========={time.ticks_diff(last_frame_ms, now)} ms")
        last_frame_ms = now

    # Mode 1,2,3
    else:
        if spi_frame_get(image_frame, width*height*2, 0) == 0:
            t1=time.ticks_ms();dbg_time("spi_cap", t1-t0);t0=t1
            if PREVIEW_TEMP:
                gray = np.frombuffer(image_frame, dtype=np.uint16).reshape((height, width))
                raw_t_min, raw_t_max = gray.min(), gray.max()
                current_temp_diff = (raw_t_max - raw_t_min) / 64.0
                img_8bit = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
                img_8bit_raw_min_max = (img_8bit.min(), img_8bit.max())
                t1=time.ticks_ms();dbg_time("normalize", t1-t0);t0=t1

                # 【修改】根据不同模式判断是否启用 SR
                current_sr_enable = False
                if mode == 1:
                    current_sr_enable = state['sr_therm']
                elif mode == 2:
                    current_sr_enable = state['sr_mix']
                elif mode == 3:
                    current_sr_enable = state['sr_edge']

                if current_sr_enable:
                    grayimg = image.cv2image(img_8bit).resize(256, 192)
                    results = x3model.forward_image(grayimg)
                    t1=time.ticks_ms();dbg_time("sr infer", t1-t0);t0=t1
                    x3out = results[output_layer_name]
                    x3grayimg_np = tensor.tensor_to_numpy_uint8(x3out, copy=False).reshape((480, 640))
                    x3grayimg_np = x3grayimg_np.astype(np.uint8)
                    t1=time.ticks_ms();dbg_time("sr out", t1-t0);t0=t1
                    final_thermal_gray = cv2.resize(x3grayimg_np, (disp.width(), disp.height()))
                    t1=time.ticks_ms();dbg_time("sr resize", t1-t0);t0=t1
                    final_thermal_gray = scale_to_range(final_thermal_gray, img_8bit_raw_min_max[0], img_8bit_raw_min_max[1]).astype(np.uint8)
                    t1=time.ticks_ms();dbg_time("sr scale", t1-t0);t0=t1
                else:
                    final_thermal_gray = cv2.resize(img_8bit, (disp.width(), disp.height()))
                    t1=time.ticks_ms();dbg_time("no sr resize", t1-t0);t0=t1
                
                final_img_np = None
                current_cmap_id = CMAP_LIST[state['cmap_idx']][1]

                if mode == 1: # Therm
                    final_img_np = cv2.applyColorMap(final_thermal_gray, current_cmap_id)
                    t1=time.ticks_ms();dbg_time("Therm cmap", t1-t0);t0=t1

                else:
                    cam_img = None
                    if cam:
                        try: cam_img = cam.read()
                        except: pass
                    t1=time.ticks_ms();dbg_time("cam cap", t1-t0);t0=t1

                    vis_aligned = None
                    if cam_img is not None:
                        vis_np = image.image2cv(cam_img, ensure_bgr=True)
                        t1=time.ticks_ms();dbg_time("cam2cv", t1-t0);t0=t1
                        vis_aligned = align_camera_image(vis_np, disp.width(), disp.height(), state['scale'], state['x'], state['y'])
                        t1=time.ticks_ms();t0=t1

                    if vis_aligned is None:
                        final_img_np = cv2.applyColorMap(final_thermal_gray, current_cmap_id)
                        t1=time.ticks_ms();dbg_time("cam cmap", t1-t0);t0=t1
                    elif mode == 2: # Mix
                        therm_color = cv2.applyColorMap(final_thermal_gray, current_cmap_id)
                        t1=time.ticks_ms();dbg_time("cam cmap1", t1-t0);t0=t1
                        final_img_np = process_adaptive_mix(vis_aligned, final_thermal_gray, therm_color, current_temp_diff)
                        t1=time.ticks_ms();dbg_time("process_adaptive_mix", t1-t0);t0=t1
                    elif mode == 3: # Edge
                        final_img_np = process_edge_fusion(vis_aligned, final_thermal_gray, raw_t_min, raw_t_max)
                        t1=time.ticks_ms();dbg_time("process_edge_fusion", t1-t0);t0=t1

                img = image.cv2image(final_img_np)
                t1=time.ticks_ms();dbg_time("cv2image", t1-t0);t0=t1
                draw_ui(img, disp.width(), disp.height(), state, current_temp_diff)
                t1=time.ticks_ms();dbg_time("ui", t1-t0);t0=t1
                disp.show(img)
                t1=time.ticks_ms();dbg_time("show", t1-t0);t0=t1

                now = time.ticks_ms()
                # 帧率计算修正为 (last, now)
                print(f"==========={time.ticks_diff(last_frame_ms, now)} ms")
                last_frame_ms = now
        else:
            time.sleep(0.05)

    process_touch(ts, disp.width(), disp.height(), state)

app.set_sys_config_kv("npu", "ai_isp", str(old_ai_isp))
save_config(state)
