from maix import pinmap
from maix import i2c, spi
from maix import time

PREVIEW_TEMP = True
FRAME_NUM = 0
Vtemp = 0

pin_function = {
    "A8": "I2C7_SCL",
    "A9": "I2C7_SDA",
    "B21": "SPI2_CS1",
    "B19": "SPI2_MISO",
    "B18": "SPI2_MOSI",
    "B20": "SPI2_SCK"
}

for pin, func in pin_function.items():
    if 0 != pinmap.set_pin_function(pin, func):
        print(f"Failed: pin{pin}, func{func}")
        exit(-1)

###############################################################################
bus = i2c.I2C(7, i2c.Mode.MASTER)
slaves = bus.scan()
print("find slaves:")
for s in slaves:
    print(f"{s}[0x{s:02x}]")

# 0x3c

# more API see https://wiki.sipeed.com/maixpy/api/maix/peripheral/i2c.html

###############################################################################
spidev = spi.SPI(2, spi.Mode.MASTER, 30000000, 1, 1, hw_cs=1)

BUFF_LEN = 4096
DUMMY_LEN = 512

def SPIDataRW(spi_id, tx_data: bytearray, rx_data: bytearray, length: int):
    """
    spi_id: 保留参数，未使用
    tx_data: 要发送的数据（bytearray）
    rx_data: 用于接收数据（bytearray，长度应为 length）
    length: 发送/接收的数据长度
    """
    # 只取前 length 字节发送
    to_send = bytes(tx_data[:length])
    # 调用底层 SPI 读写
    result = spidev.write_read(to_send, length)
    # 将结果写入 rx_data
    rx_data[:length] = result

def spi_frame_get(raw_frame: bytearray, frame_byte_size: int, frame_type: int) -> int:
    tx_Data = bytearray(BUFF_LEN)
    rx_Data = bytearray(BUFF_LEN)
    i = 0
    new_frame_cmd = 0
    continue_cmd = 0x55

    if frame_type == 0:
        new_frame_cmd = 0xAA
    elif frame_type == 1:
        new_frame_cmd = 0xCC

    tx_Data[0] = new_frame_cmd
    SPIDataRW(0, tx_Data, rx_Data, BUFF_LEN)
    # start from dummy and header
    raw_frame[i:i + BUFF_LEN - DUMMY_LEN] = rx_Data[DUMMY_LEN:BUFF_LEN]
    i += BUFF_LEN - DUMMY_LEN

    if rx_Data[480] != 1:
        return -1

    global FRAME_NUM
    global Vtemp
    FRAME_NUM = (rx_Data[480+2] & 0xff) + rx_Data[480+3] * 256
    shutter_state = rx_Data[480+4]
    Vtemp = rx_Data[480+5] + rx_Data[480+6] * 256
    gain_state = rx_Data[480+9]
    pix_freeze_state = rx_Data[480+12]
    print(f"frame num={FRAME_NUM}, shutter={shutter_state}, Vtemp={Vtemp}, gain={gain_state}, freeze={pix_freeze_state}")

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

###############################################################################
wh = [0x1d, 0x00]
rh = [0x1d, 0x08]
# # d = [0x05, 0x84, 0x04, 0x00, 0x00, 0x04, 0x00, 0x04] # PROJECT_INFO
# # d = [0x05, 0x84, 0x06, 0x00, 0x00, 0x30, 0x00, 0x30] # GET_PN
# d = [0x05, 0x84, 0x07, 0x00, 0x00, 0x10, 0x00, 0x10] # GET_SN
# rl = d[6]*256+d[7]

# r = bus.writeto(0x3c, bytes(wh+d))
# print(r)
# r = bus.writeto(0x3c, bytes(rh))
# print(r)
# time.sleep(1)
# r = bus.readfrom(0x3c, rl)
# print(r)

# # VCMD_SPI_DEFAULT_RESTORE
# d = [0x01, 0x0e, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

# r = bus.writeto(0x3c, bytes(wh+d))
# print(r)

# VCMD_PREVIEW_STOP
print("VCMD_PREVIEW_STOP")
d = [0x0f, 0x02, 0x00, 0x00, 0x00, 0x00, 0x08, 0x00]

r = bus.writeto(0x3c, bytes(wh+d))
print(r)
time.sleep(1)

# VCMD_PREVIEW_START
print("VCMD_PREVIEW_START")
path = 0 # 0x0 : VOC1,    0x1 : VOC2
src = 0 # 0x0 : IR,    0x80 : fix pattern
width = 256
height = 192
fps = 25
mode = 8 # 0 dvp , 8 spi
d = [0x0f, 0xc1, 0x00, 0x00, 0x00, 0x00, 0x08, 0x00,
    path, src, width>>8, width&0xff, height>>8, height&0xff, fps, mode]

r = bus.writeto(0x3c, bytes(wh+d))
print(r)
time.sleep(5)

# typedef struct
# {
# 	uint8_t		byCmdType;
# 	uint8_t		bySubCmd;
# 	uint8_t		byPara;
# 	uint8_t		byAddr_h;
# 	uint8_t		byAddr_l;
# 	uint8_t		byAddr_ll;
# 	uint8_t		byLen_h;
# 	uint8_t		byLen_l;
# }vdcmd_std_header_t;

# VCMD_TEMP_PREVIEW_START
d = [0x0a, 0x01 if PREVIEW_TEMP else 0x02, path, 0x00, 0x00, 0x00, 0x00, 0x00]

r = bus.writeto(0x3c, bytes(wh+d))
print(r)
time.sleep(2)

# print("get_prop_auto_shutter_params------------")
# d = [0x14, 0x82, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00] + [0, 0, 0, 0, 0, 0, 0, 2]

# r = bus.writeto(0x3c, bytes(wh+d))
# print(r)
# r = bus.writeto(0x3c, bytes(rh))
# print(r)
# rl = d[-2]*256+d[-1]
# r = bus.readfrom(0x3c, rl)
# print(r)
# print("get_prop_auto_shutter_params------------")

if not PREVIEW_TEMP:
    # print("pseudo_color_get")
    # d = [0x09, 0x84, path, 0x00, 0x00, 0x00, 0x00, 0x01]

    # r = bus.writeto(0x3c, bytes(wh+d))
    # print(r)
    # r = bus.writeto(0x3c, bytes(rh))
    # print(r)
    # rl = d[6]*256+d[7]
    # r = bus.readfrom(0x3c, rl)
    # print(r)
    # time.sleep(1)

    print("pseudo_color_set")
    d = [0x09, 0xc4, path, 0x00, 0x00, 0x00, 0x00, 0x01, 0x01]

    r = bus.writeto(0x3c, bytes(wh+d))
    print(r)
    time.sleep(1)

    # print("pseudo_color_get")
    # d = [0x09, 0x84, path, 0x00, 0x00, 0x00, 0x00, 0x01]

    # r = bus.writeto(0x3c, bytes(wh+d))
    # print(r)
    # r = bus.writeto(0x3c, bytes(rh))
    # print(r)
    # rl = d[6]*256+d[7]
    # r = bus.readfrom(0x3c, rl)
    # print(r)

###############################################################################
# print("start fetch frame")

# for i in range(4):
#     image_frame = bytearray(width*height*2)
#     if spi_frame_get(image_frame, width*height*2, 0) == 0: #src picture
#         print("fetched one frame")
#         open(f"/root/a{i}.yuv", "wb").write(image_frame)

# print("stop fetch frame")

###############################################################################

def scale_to_range(arr, target_min, target_max):
    """
    将NumPy数组缩放到[target_min, target_max]范围
    
    参数:
        arr: 输入的NumPy数组
        target_min: 目标范围的最小值
        target_max: 目标范围的最大值
    
    返回:
        缩放后的NumPy数组
    """
    # 获取原始数组的最小值和最大值
    original_min = arr.min()
    original_max = arr.max()
    
    # 处理数组所有元素相等的特殊情况
    if original_min == original_max:
        return np.full_like(arr, target_min)
    
    # 线性缩放公式
    scaled_arr = (arr - original_min) / (original_max - original_min) * (target_max - target_min) + target_min
    return scaled_arr


from maix import display, app, image, camera, nn, tensor, touchscreen
import numpy as np
import cv2
import time
import inspect

need_exit = 0
hide_hud = False
enable_x3 = True
ts = touchscreen.TouchScreen()

disp = display.Display()
print("display init done")
print(f"display size: {disp.width()}x{disp.height()}")
cam = camera.Camera(disp.width(), disp.height())    # Manually set resolution
                                                    # | 手动设置分辨率

img = cam.read()
disp.show(img)

x3model_name = './x3c_192x256.mud'
# x3model_name = './espcn_x3.mud'

x3model = nn.NN(x3model_name)
if x3model_name == './espcn_x3.mud':
    output_layer_name = '19'
elif x3model_name == './x3c_192x256.mud':
    output_layer_name = 'image_output'
else:
    raise RuntimeError("Unsupported x3 model")

image_frame = bytearray(width*height*2)
while not app.need_exit():
    img = cam.read()
    img.draw_string(img.width()//2, img.height()//2, "Error: Init Failed.", image.Color.from_rgb(255, 0, 0))
    gray = np.array([])
    a0 = time.perf_counter()
    if spi_frame_get(image_frame, width*height*2, 0) == 0: #src picture
        # print(f"{inspect.currentframe().f_lineno}: 耗时: {time.perf_counter() - a0:.6f} 秒")

        # if FRAME_NUM % 50 == 0:
        #     d = [0x0d, 0xc1, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        #     r = bus.writeto(0x3c, bytes(wh+d))
        #     print(r)

        if PREVIEW_TEMP:
            gray = np.frombuffer(image_frame, dtype=np.uint16).reshape((height, width))
            # gray = cv2.rotate(gray, cv2.ROTATE_180)

            # 归一化到8位（0~255）
            img_8bit = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            img_8bit_raw_min_max = (img_8bit.min(), img_8bit.max())

            if enable_x3:
                grayimg = image.cv2image(img_8bit).resize(256, 192)
                x3graytensors = x3model.forward_image(grayimg)
                x3graytensor = x3graytensors[output_layer_name]
                if x3model_name == './espcn_x3.mud':
                    x3grayimg_np = tensor.tensor_to_numpy_float32(x3graytensor, copy = False).reshape((576, 768))
                elif x3model_name == './x3c_192x256.mud':
                    x3grayimg_np = tensor.tensor_to_numpy_uint8(x3graytensor, copy = False).reshape((576, 768))
                else:
                    raise RuntimeError("Unsupported x3 model")
                x3grayimg_np = x3grayimg_np.astype(np.uint8)


                img_8bit = cv2.resize(x3grayimg_np, (disp.width(), disp.height()))

                img_8bit = scale_to_range(img_8bit, img_8bit_raw_min_max[0], img_8bit_raw_min_max[1]).astype(np.uint8)
            else:
                img_8bit = cv2.resize(img_8bit, (disp.width(), disp.height()))

            # 伪彩色映射（热力图）
            color_img = cv2.applyColorMap(img_8bit, cv2.COLORMAP_MAGMA)  # BGR格式 COLORMAP_HOT COLORMAP_TURBO
            color_img = image.cv2image(color_img)

            center_pos = (height//2, width//2)
            center_temp = gray[center_pos] / 64 - 273.15
            # print(f"c: {center_temp:.3f} ({center_pos})")
            color_img.draw_cross(int(color_img.width()*(center_pos[1]/width)), int(color_img.height()*(center_pos[0]/height)), image.COLOR_GREEN, size=8, thickness=3)
            color_img.draw_circle(int(color_img.width()*(center_pos[1]/width)), int(color_img.height()*(center_pos[0]/height)), 4, image.COLOR_GREEN, thickness=3)
            color_img.draw_string(int(color_img.width()*(center_pos[1]/width)), int(color_img.height()*(center_pos[0]/height)) + 30, f"{center_temp:.1f}", image.COLOR_GREEN, scale=2, thickness=2)

            min_pos, max_pos = np.unravel_index(np.argmin(gray), gray.shape), np.unravel_index(np.argmax(gray), gray.shape)
            min_temp, max_temp = (gray[min_pos] / 64 - 273.15), (gray[max_pos] / 64 - 273.15)

            color_img.draw_cross(int(color_img.width()*(max_pos[1]/width)), int(color_img.height()*(max_pos[0]/height)), image.COLOR_WHITE, size=8, thickness=3)
            color_img.draw_string(int(color_img.width()*(max_pos[1]/width)), int(color_img.height()*(max_pos[0]/height)) + 30, f"H:{max_temp:.1f}", image.COLOR_WHITE, scale=2, thickness=2)

            color_img.draw_cross(int(color_img.width()*(min_pos[1]/width)), int(color_img.height()*(min_pos[0]/height)), image.COLOR_BLUE, size=8, thickness=3)
            color_img.draw_string(int(color_img.width()*(min_pos[1]/width)), int(color_img.height()*(min_pos[0]/height)) + 30, f"L:{min_temp:.1f}", image.COLOR_BLUE, scale=2, thickness=2)

        else:
            # # 1. 转为 numpy 数组
            # yuyv = cv2.flip(np.frombuffer(image_frame, dtype=np.uint8).reshape((height, width, 2)), -1)
            # # 2. 转为 BGR（OpenCV 默认）
            # bgr_img = cv2.cvtColor(yuyv, cv2.COLOR_YUV2BGR_YUYV)[::-1,::-1]
            # color_img = bgr_img
            # # 3. 提取灰度（Y通道）
            # gray = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2GRAY)


            yuyv = np.frombuffer(image_frame, dtype=np.uint8).reshape((height, width, 2))
            gray = yuyv[::-1,::-1,0]
            gray_raw_min_max = (gray.min(), gray.max())

            if enable_x3:
                grayimg = image.cv2image(gray).resize(256, 192)
                x3graytensors = x3model.forward_image(grayimg)
                x3graytensor = x3graytensors['image_output']
                x3grayimg_np = tensor.tensor_to_numpy_uint8(x3graytensor, copy = False).reshape((576, 768))

                gray = cv2.resize(x3grayimg_np, (disp.width(), disp.height()))

                gray = scale_to_range(gray, gray_raw_min_max[0], gray_raw_min_max[1]).astype(np.uint8)
            else:
                gray = cv2.resize(gray, (disp.width(), disp.height()))

            # 4. 伪彩色映射
            color_img = cv2.applyColorMap(gray, cv2.COLORMAP_JET)  # BGR 格式
            color_img = image.cv2image(color_img)

        # img.draw_image(0, 0, color_img)
        img = color_img

        # print(f"{inspect.currentframe().f_lineno}: 耗时: {time.perf_counter() - a0:.6f} 秒")

    x, y, pressed = ts.read()
    if not pressed:
        need_exit = 0
    else:
        if need_exit or (x >= 0 and x <= 80 and y >= 0 and y <= 40): # Back
            need_exit += 1
        else:
            if x >= img.width()-120 and x <= img.width() and y >= 0 and y <= 40: # Capture
                img_bgr = image.image2cv(img, ensure_bgr=True, copy=True)
                img_bgr = cv2.resize(img_bgr, (768, 576) if enable_x3 else (256, 192))
                from datetime import datetime  # 用于处理时间戳
                filepath= "/maixapp/share/picture/thermal"
                filename = f"thermal({'x3' if enable_x3 else 'raw'})_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{FRAME_NUM}.jpg"
                import os
                targetfile = os.path.join(filepath, filename)
                os.system(f"mkdir -p {filepath}")
                
                cv2.imwrite(targetfile, img_bgr)
                # 强制刷新文件系统缓存（确保数据写入磁盘）
                os.fsync(os.open(targetfile, os.O_RDWR))
                img.draw_string(40, img.height()//2,  f"Capture to {targetfile}!", image.Color.from_rgb(255, 0, 0), scale=3, thickness=2)

                filename = f"thermal({'x3' if enable_x3 else 'raw'})_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{FRAME_NUM}.npy"
                targetfile = os.path.join(filepath, filename)
                np.save(targetfile, gray)
                os.fsync(os.open(targetfile, os.O_RDWR))
            elif x >= 0 and x <= 120 and y >= img.height()-40 and y <= img.height(): # Lo-Res
                enable_x3 = False
            elif x >= img.width()-120 and x <= img.width() and y >= img.height()-40 and y <= img.height(): # Hi-Res
                enable_x3 = True
            elif x >= img.width()//2-60 and x <= img.width()//2+60 and y >= 0 and y <= 40: # Hide HUD
                hide_hud = True
            elif x >= img.width()//2-60 and x <= img.width()//2+60 and y >= img.height()-40 and y <= img.height(): # Show HUD
                hide_hud = False
            else:
                pass
        
        if need_exit >= 15:
            app.set_exit_flag(True)

    if not hide_hud:
        img.draw_string(               10,              10, "Quit(Holding)", image.Color.from_rgb(255, 0 if need_exit == 0 else 255, 0), scale=2, thickness=2)
        img.draw_string(  img.width()-140,              10,       "Capture", image.Color.from_rgb(255, 0, 0), scale=2, thickness=2)
        img.draw_string(               10, img.height()-20,        "Lo-Res", image.Color.from_rgb(255, 0, 0), scale=2, thickness=2)
        img.draw_string(  img.width()-120, img.height()-20,        "Hi-Res", image.Color.from_rgb(255, 0, 0), scale=2, thickness=2)
        img.draw_string(img.width()//2-60,              10,      "Hide HUD", image.Color.from_rgb(255, 0, 0), scale=2, thickness=2)
        img.draw_string(img.width()//2-60, img.height()-20,      "Show HUD", image.Color.from_rgb(255, 0, 0), scale=2, thickness=2)
    disp.show(img)

# /64 - 273.15