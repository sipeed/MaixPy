# dp_eh204l_label_printer.py
# DP-EH204L 标签打印指令生成工具
import enum
from maix import uart, pinmap, time, image
import numpy as np
import cv2

def atkinson_dithering(image):
    """
    Atkinson抖动算法（Macintosh风格）
    产生更艺术化的效果
    """
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    img_float = image.astype(np.float32) / 255.0
    h, w = img_float.shape

    output = img_float.copy()

    for y in range(h):
        for x in range(w):
            old_pixel = output[y, x]
            new_pixel = 1.0 if old_pixel > 0.5 else 0.0
            output[y, x] = new_pixel

            quant_error = old_pixel - new_pixel

            # Atkinson误差扩散核
            # 扩散1/8的误差到更多像素
            if x < w - 1:
                output[y, x + 1] += quant_error / 8
            if x < w - 2:
                output[y, x + 2] += quant_error / 8
            if y < h - 1:
                if x > 0:
                    output[y + 1, x - 1] += quant_error / 8
                output[y + 1, x] += quant_error / 8
                if x < w - 1:
                    output[y + 1, x + 1] += quant_error / 8
            if y < h - 2:
                output[y + 2, x] += quant_error / 8

    output = np.clip(output * 255, 0, 255).astype(np.uint8)
    return output

def multi_level_dithering(image, levels=4):
    """
    多级灰度抖动
    levels: 输出灰度级数（2-256）
    """
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    h, w = image.shape

    # 生成Bayer矩阵
    n = int(np.sqrt(levels - 1))
    bayer_size = 2
    while bayer_size < n:
        bayer_size *= 2

    # 创建Bayer矩阵
    if bayer_size == 2:
        bayer = np.array([[0, 2], [3, 1]])
    else:
        # 递归生成更大的Bayer矩阵
        bayer = np.zeros((bayer_size, bayer_size), dtype=np.float32)
        sub_size = bayer_size // 2
        sub_bayer = multi_level_dithering(np.ones((sub_size, sub_size)) * 128,
                                          levels=sub_size**2 + 1)
        bayer = sub_bayer.astype(np.float32) / 255.0 * (bayer_size**2 - 1)

    # 扩展Bayer矩阵
    bayer_h, bayer_w = bayer.shape
    bayer_tiled = np.tile(bayer, (h // bayer_h + 1, w // bayer_w + 1))[:h, :w]

    # 归一化Bayer矩阵
    bayer_norm = bayer_tiled / (bayer_size**2)

    # 应用抖动
    img_norm = image.astype(np.float32) / 255.0
    dithered = np.floor(img_norm * (levels - 1) + bayer_norm) / (levels - 1)

    return (dithered * 255).astype(np.uint8)


def floyd_steinberg_dithering(image, levels=2):
    """
    Floyd-Steinberg抖动算法
    levels: 输出灰度级数（2表示黑白）
    """
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    img_float = image.astype(np.float32) / 255.0
    h, w = img_float.shape

    # 复制图像进行处理
    output = img_float.copy()

    # 量化步长
    step = 1.0 / (levels - 1)

    for y in range(h):
        for x in range(w):
            old_pixel = output[y, x]

            # 找到最近的量化级别
            new_pixel = np.round(old_pixel / step) * step
            output[y, x] = new_pixel

            # 计算量化误差
            quant_error = old_pixel - new_pixel

            # 扩散误差到相邻像素（Floyd-Steinberg核）
            if x < w - 1:
                output[y, x + 1] += quant_error * 7/16
            if y < h - 1:
                if x > 0:
                    output[y + 1, x - 1] += quant_error * 3/16
                output[y + 1, x] += quant_error * 5/16
                if x < w - 1:
                    output[y + 1, x + 1] += quant_error * 1/16

    # 转换为0-255范围
    output = np.clip(output * 255, 0, 255).astype(np.uint8)

    return output

def ordered_dithering(image, bayer_size=4):
    """
    有序抖动（Bayer抖动）
    bayer_size: Bayer矩阵大小（2, 4, 8等）
    """
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    h, w = image.shape

    # 定义Bayer矩阵（归一化到0-1）
    if bayer_size == 2:
        bayer_matrix = np.array([[0, 2],
                                 [3, 1]]) / 4.0
    elif bayer_size == 4:
        bayer_matrix = np.array([[0, 8, 2, 10],
                                 [12, 4, 14, 6],
                                 [3, 11, 1, 9],
                                 [15, 7, 13, 5]]) / 16.0
    elif bayer_size == 8:
        bayer_matrix = np.array([
            [0, 32, 8, 40, 2, 34, 10, 42],
            [48, 16, 56, 24, 50, 18, 58, 26],
            [12, 44, 4, 36, 14, 46, 6, 38],
            [60, 28, 52, 20, 62, 30, 54, 22],
            [3, 35, 11, 43, 1, 33, 9, 41],
            [51, 19, 59, 27, 49, 17, 57, 25],
            [15, 47, 7, 39, 13, 45, 5, 37],
            [63, 31, 55, 23, 61, 29, 53, 21]
        ]) / 64.0
    else:
        raise ValueError('')

    # 扩展Bayer矩阵到图像大小
    bayer_h, bayer_w = bayer_matrix.shape
    tile_y = np.tile(bayer_matrix, (h // bayer_h + 1, w // bayer_w + 1))
    bayer_tiled = tile_y[:h, :w]

    # 归一化图像到0-1
    img_normalized = image.astype(np.float32) / 255.0

    # 应用抖动
    dithered = np.where(img_normalized > bayer_tiled, 1.0, 0.0)

    return (dithered * 255).astype(np.uint8)


class DPEH204L:
    def __init__(self):
        pinmap.set_pin_function("B0", "UART2_TX")
        pinmap.set_pin_function("B1", "UART2_RX")

        device = "/dev/ttyS2"
        self.serial = uart.UART(device, 1500000)
        self.max_w = 384
        self.max_h = 256

    def serial_write(self, label_data:bytes):
        curr_baudrate = self.serial.get_baudrate()
        delay_ms = 1024 // (curr_baudrate // 10000) + 1
        for i in range(0, len(label_data), 1024):
            remaining = 1024 if (i + 1024) <= len(label_data) else len(label_data) - i
            print(f'[{i}:{i + remaining}]')
            self.serial.write(label_data[i:i + remaining])
            time.sleep_ms(delay_ms)

    def init_label(self):
        return bytes([0x1B, 0x40])

    def start_label(self, x, y, width, height, rotate=0):
        """
        标签开始指令
        x, y: 标签面参考原点相对标签纸当前位置左上角的偏移量（单位：）  range:[1576/384]???
        width, height: 标签面页宽和页高（单位：点） [1, 1200]
        rotate: 旋转角度 {0,1,2,3}
        1点 = 0.125mm
        """
        return bytes([0x1A, 0x5B, 0x01,
                    x & 0xFF, (x >> 8) & 0xFF,
                    y & 0xFF, (y >> 8) & 0xFF,
                    width & 0xFF, (width >> 8) & 0xFF,
                    height & 0xFF, (height >> 8) & 0xFF,
                    rotate & 0xFF])

    def end_label(self):
        """标签结束指令"""
        return bytes([0x1A, 0x5D, 0x00])

    def print_num(self, times=1):
        """
        标签打印指令
        times: 打印次数，1-255
        """
        if times == 1:
            return bytes([0x1A, 0x4F, 0x00])
        else:
            return bytes([0x1A, 0x4F, 0x01, times & 0xFF])

    def draw_text(self, x, y, text, font_type=0x00, encoding='gbk'):
        """
        标签文本打印指令
        x, y: 文本起始位置（单位：点）
        text: 要打印的文本字符串
        font_type: 字体类型和样式（参考文档中的 FontType_L/FontType_H）
        encoding: 文本编码，默认为 GBK（中文支持）
        """
        text_bytes = text.encode(encoding) + b'\x00'
        if font_type == 0x00:
            # 简单文本模式
            return bytes([0x1A, 0x54, 0x00,
                        x & 0xFF, (x >> 8) & 0xFF,
                        y & 0xFF, (y >> 8) & 0xFF]) + text_bytes
        else:
            # 带字体类型模式
            return bytes([0x1A, 0x54, 0x01,
                        x & 0xFF, (x >> 8) & 0xFF,
                        y & 0xFF, (y >> 8) & 0xFF,
                        0x18, 0x00,
                        font_type & 0xFF, (font_type >> 8) & 0xFF]) + text_bytes

    def draw_line(self, x1, y1, x2, y2, width=1, color=1):
        """
        绘制线段指令（带线宽和颜色）
        x1, y1: 起点坐标
        x2, y2: 终点坐标
        width: 线宽（1-255）
        color: 0=白色，1=黑色
        """
        return bytes([0x1A, 0x5C, 0x01,
                    x1 & 0xFF, (x1 >> 8) & 0xFF,
                    y1 & 0xFF, (y1 >> 8) & 0xFF,
                    x2 & 0xFF, (x2 >> 8) & 0xFF,
                    y2 & 0xFF, (y2 >> 8) & 0xFF,
                    width & 0xFF, (width >> 8) & 0xFF,
                    color & 0xFF])

    def draw_rect(self, left, top, right, bottom, width=1, color=1):
        """
        绘制矩形框指令
        left, top: 左上角坐标
        right, bottom: 右下角坐标
        width: 线宽
        color: 0=白色，1=黑色
        """
        return bytes([0x1A, 0x26, 0x01,
                    left & 0xFF, (left >> 8) & 0xFF,
                    top & 0xFF, (top >> 8) & 0xFF,
                    right & 0xFF, (right >> 8) & 0xFF,
                    bottom & 0xFF, (bottom >> 8) & 0xFF,
                    width & 0xFF, (width >> 8) & 0xFF,
                    color & 0xFF])

    def draw_barcode(self, x, y, barcode_type, height, unit_width, rotate, data):
        """
        一维条码打印指令
        x, y: 条码左上角坐标
        barcode_type: 条码类型（0-29，参考文档）
        height: 条码高度
        unit_width: 码宽（1-4）
        rotate: 旋转角度（0-3）
        data: 条码数据字符串
        """
        data_bytes = data.encode('ascii') + b'\x00'
        return bytes([0x1A, 0x30, 0x00,
                    x & 0xFF, (x >> 8) & 0xFF,
                    y & 0xFF, (y >> 8) & 0xFF,
                    barcode_type & 0xFF,
                    height & 0xFF,
                    unit_width & 0xFF,
                    rotate & 0xFF]) + data_bytes

    def draw_qrcode(self, x, y, version, ecc, unit_width, rotate, data):
        """
        QRCode二维码打印指令
        x, y: 二维码左上角坐标
        version: 版本（0-20，0为自动）
        ecc: 纠错等级（1-4）
        unit_width: 码块大小（1-8）
        rotate: 旋转角度（0-3）
        data: 二维码内容字符串
        """
        data_bytes = data.encode('gbk') + b'\x00'
        return bytes([0x1A, 0x31, 0x00,
                    version & 0xFF,
                    ecc & 0xFF,
                    x & 0xFF, (x >> 8) & 0xFF,
                    y & 0xFF, (y >> 8) & 0xFF,
                    unit_width & 0xFF,
                    rotate & 0xFF]) + data_bytes

    def draw_bitmap(self, x, y, width, height, data, show_type=1):
        """
        位图打印指令
        x, y: 位图左上角坐标
        width: 位图像素宽度
        height: 位图像素高度
        data: 位图点阵数据（字节流）
        show_type: 0=正常，1=反白
        """

        # # 位图像素宽度需除以8
        # if width % 8 == 0:
        #     width = width // 8
        # else:
        #     width = width // 8 + 1

        cmd = bytes([0x1A, 0x21, 0x01])
        
        return cmd + bytes([
            x & 0xFF, (x >> 8) & 0xFF,
            y & 0xFF, (y >> 8) & 0xFF,
            width & 0xFF, (width >> 8) & 0xFF,
            height & 0xFF, (height >> 8) & 0xFF,
            show_type & 0xFF, 0x0
        ]) + data

    def label_calibration(self):
        """标签校准指令"""
        return bytes([0x1F, 0x63])

    def check_paper_status(self):
        """检查缺纸状态指令"""
        return bytes([0x10, 0x04, 0x01])

    def set_baudrate(self, new_baudrate):
        m = 5
        # 实测最高到1500000
        baudrate_list = [1200, 2400, 3600, 4800, 7200, 9600, 14400, 19200, 28800, 38400, 57600, 76800, 115200, 153600, 230400, 307200, 460800, 614400, 921600, 122800, 1843200]
        for m, baudrate in enumerate(baudrate_list):
            if baudrate == new_baudrate:
                print(f'Set baudrate to {baudrate}, m = {m}')
                cmd = bytes([0x1f, 0x2d, 0x55, 0x01, m])
                self.serial_write(cmd)
                self.serial.set_baudrate(baudrate)
                print('serial current baudrate:', self.serial.get_baudrate())
                return
        raise ValueError(f'Not support baudrate: {new_baudrate}')
        
    def create_sample_label(self):
        """
        创建一个示例标签，包含文本、矩形框、条码和二维码
        """
        # 标签开始：384点宽，200点高
        label_data = self.start_label(0, 0, 384, 200)
        self.print_bytes(label_data)

        # 绘制边框
        # label_data += self.draw_rect(0, 0, 384, 195, width=2, color=1)
        
        # # 打印标题文本（字体放大）
        # label_data += self.draw_text(100, 20, "产品标签", font_type=0x0011, encoding='gbk')
        
        # # 绘制分隔线
        # label_data += self.draw_line(10, 50, 374, 50, width=1, color=1)
        
        # 打印产品信息
        data = self.draw_text(20, 70, "产品名称：样品A", font_type=0x0000, encoding='gbk')
        self.print_bytes(data)
        label_data += data
        
        data = self.draw_text(20, 100, "生产日期：2024-01-01", font_type=0x0000, encoding='gbk')
        self.print_bytes(data)
        label_data += data

        # data = self.draw_text(20, 130, "批号：20240101001", font_type=0x0000, encoding='gbk')
        # self.print_bytes(data)
        # label_data += data
        
        # 打印一维条码（Code 128）
        label_data += self.draw_barcode(250, 60, 8, 40, 2, 0, "20240101001")
        
        # 打印二维码
        label_data += self.draw_qrcode(250, 110, 5, 3, 4, 0, "https://example.com/product/A")
        
        # 标签结束
        data = self.end_label()
        self.print_bytes(data)
        label_data += data

        # 打印一次
        data = self.print_num(1)
        self.print_bytes(data)
        label_data += data

        return label_data

    def print_bytes(self, data):
        for byte in data:
            print(f"{byte:#x}", end=' ')
        print('')

    def img_to_bitmap(self, img: image.Image):
        if img.format() != image.Format.FMT_GRAYSCALE:
            gray_img = img.to_format(image.Format.FMT_GRAYSCALE)
        else:
            gray_img = img

        bitmap = []
        byte = 0
        for h in range(gray_img.height()):
            for w in range(gray_img.width()):
                bit = 1 if gray_img.get_pixel(w, h)[0] > 127 else 0
                bit_num = w % 8
                byte |= bit << (7 - bit_num)
                if (w + h * gray_img.width() + 1) % 8 == 0 or w == gray_img.width() - 1:
                    bitmap.append(byte)
                    byte = 0
        return bytes(bitmap)

    def bitmap_to_img(self, bitmap, width, height):
        img_bytes = []
        for h in range(height):
            for w in range(width // 8):
                data = bitmap[w + h * width // 8]
                for i in range(8):
                    if (data >> i) & 1 == 1:
                        img_bytes.append(255)
                    else:
                        img_bytes.append(0)
        return image.from_bytes(width, height, image.Format.FMT_GRAYSCALE, bytes(img_bytes))

    def create_image_cmd(self, img: image.Image):
        print('img data size:', img.data_size())


        bitmap = self.img_to_bitmap(img)
        """
        创建一个示例标签，包含图片
        """
        label_data = self.init_label()

        label_data += self.start_label(0, 0, self.max_w, self.max_h)
        
        # 绘制边框
        x = (self.max_w - img.width()) // 2
        y = (self.max_h - img.height()) // 2
        label_data += self.draw_bitmap(x, y, img.width(), img.height(), data=bitmap)

        # 标签结束
        label_data += self.end_label()
        
        # 打印一次
        label_data += self.print_num(1)
        
        return label_data

    def create_image_cmd_from_path(self, path:str):
        img0 = cv2.imread(path)
        img_resize = cv2.resize(img0, (224, 224))
        new_img = atkinson_dithering(img_resize)
        img = image.cv2image(new_img, bgr=True, copy=False)
        return self.create_image_cmd(img)

    def save_label_to_file(self, data, filename="label_data.bin"):
        """将标签数据保存到文件"""
        with open(filename, "wb") as f:
            f.write(data)
        print(f"标签数据已保存到 {filename}")

if __name__ == "__main__":
    """主函数：创建并保存/打印示例标签"""
    d = DPEH204L()

    img_path = '/maixapp/share/picture/2024.1.1/cat_224.jpg'
    # img0 = cv2.imread(img_path)
    # # t = time.time()
    # # new_img = multi_level_dithering(img0)
    # # print('multi_level_dithering cost:', time.time() - t)
    
    # # t = time.time()
    # # new_img = atkinson_dithering(img0)
    # # print('atkinson_dithering cost:', time.time() - t)

    # # t = time.time()
    # # new_img = ordered_dithering(img0)
    # # print('ordered_dithering cost:', time.time() - t)

    # t = time.time()
    # new_img = floyd_steinberg_dithering(img0)
    # print('floyd_steinberg_dithering cost:', time.time() - t)

    # img_show = image.cv2image(new_img, bgr=True, copy=False)
    # img_show.to_format(image.Format.FMT_RGB888).save('/root/test.jpg')
    # img = img_show
    # d.set_baudrate(1843200)

    cmd = d.create_image_cmd_from_path(img_path)
    d.serial_write(cmd)