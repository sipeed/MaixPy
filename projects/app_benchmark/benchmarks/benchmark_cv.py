

from maix import image, time, display, touchscreen, nn, tensor, app, sys
import gc
import os
import numpy as np
import cv2

class Bechmark:
    name = "CV"

    def __init__(self, disp : display.Display, ts : touchscreen.TouchScreen):
        self.warmup_times = 3
        self.repeat_times = 40
        self.disp = disp
        self.ts = ts

    def get_img_copy(self, src_img, res):
        if src_img.width() != res[0] or src_img.height() != res[1]:
            return src_img.resize(res[0], res[1], image.Fit.FIT_CONTAIN)
        else:
            return src_img.copy()

    def benchmark_openmv_find_blobs(self, items):
        img0 = image.load("/maixapp/share/picture/2024.1.1/cube_640x480.jpg")
        thresholds = [[0, 80, 40, 80, 0, 80]]  # red
        configs = [
            [320, 240, 1.3, 2, 100, 100],
            [640, 480, 2, 2, 800, 800]
        ]

        for config in configs:
            res = config[:2]
            font_scale = config[2]
            font_thickness = config[3]
            area_threshold = config[4]
            pixels_threshold = config[5]
            img = self.get_img_copy(img0, res)

            # warm up
            print("warn up")
            for i in range(self.warmup_times):
                blobs = img.find_blobs(thresholds, area_threshold=area_threshold, pixels_threshold=pixels_threshold)
            img_disp = img.copy()
            # item name
            item_name = f"find_blobs {res[0]}x{res[1]}"
            # draw results
            for b in blobs:
                corners = b.mini_corners()
                for i in range(4):
                    img_disp.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_GREEN, thickness=font_thickness)
            # draw hint
            msg = f"{item_name} ..."
            print(msg)
            size = image.string_size(msg, scale=font_scale, thickness=font_thickness)
            img_disp.draw_rect(0, (img_disp.height() - size.height()) // 2 - 10, img_disp.width(), size.height() + 20, image.COLOR_RED, thickness=-1)
            img_disp.draw_string((img_disp.width() - size.width()) // 2, (img_disp.height() - size.height()) // 2, msg, image.COLOR_WHITE, scale=font_scale, thickness=font_thickness)
            self.disp.show(img_disp)
            # run
            t_sum = 0
            print(f"run {self.repeat_times} times")
            for i in range(self.repeat_times):
                t = time.ticks_us()
                blobs = img.find_blobs(thresholds, area_threshold=area_threshold, pixels_threshold=pixels_threshold)
                t_sum += time.ticks_us() - t
            t = t_sum / self.repeat_times / 1000 # ms
            fps = 1000 // t
            items[item_name] = f"{t:.1f} ms, {fps} fps"
            print(item_name, ":", items[item_name])
            del img, img_disp
            gc.collect()
            print("end one instance")

    def benchmark_openmv_binary(self, items):
        img_rgb = image.load("/maixapp/share/picture/2024.1.1/cube_640x480.jpg")
        img_gray = img_rgb.to_format(image.Format.FMT_GRAYSCALE)
        imgs = [img_rgb, img_gray]
        ths = [[[0, 80, 40, 80, 0, 80]], [[0, 150, 0, 0, 0, 0]]]
        configs = [
            # img_idx, width, height, font_scale, font_thickness
            [0, 320, 240, 1.3, 2],
            [0, 640, 480, 2, 2],
            [1, 320, 240, 1.3, 2],
            [1, 640, 480, 2, 2]
        ]
        for config in configs:
            img_idx = config[0]
            res = config[1:3]
            font_scale = config[3]
            font_thickness = config[4]
            img = self.get_img_copy(imgs[img_idx], res)

            # warm up
            print("warn up")
            for i in range(self.warmup_times):
                img_disp = img.copy()
                img_disp.binary(ths[img_idx])
            # item name
            item_name = f"binary {'gray' if img_idx==1 else 'rgb'} {res[0]}x{res[1]}"
            # draw hint
            msg = f"{item_name} ..."
            print(msg)
            size = image.string_size(msg, scale=font_scale, thickness=font_thickness)
            img_disp.draw_rect(0, (img_disp.height() - size.height()) // 2 - 10, img_disp.width(), size.height() + 20, image.COLOR_RED, thickness=-1)
            img_disp.draw_string((img_disp.width() - size.width()) // 2, (img_disp.height() - size.height()) // 2, msg, image.COLOR_WHITE, scale=font_scale, thickness=font_thickness)
            self.disp.show(img_disp)
            # run
            t_sum = 0
            print(f"run {self.repeat_times} times")
            for i in range(self.repeat_times):
                img_disp = img.copy()
                t = time.ticks_us()
                img_disp.binary(ths[img_idx])
                t_sum += time.ticks_us() - t
            t = t_sum / self.repeat_times / 1000
            fps = 1000 // t
            items[item_name] = f"{t:.1f} ms, {fps} fps"
            print(item_name, ":", items[item_name])
            del img, img_disp
            gc.collect()
            print("end one instance")

    def benchmark_openmv_hist(self, items):
        img = image.load("/maixapp/share/picture/2024.1.1/cube_640x480.jpg")
        img = img.to_format(image.Format.FMT_GRAYSCALE)
        configs = [
            # width, height, font_scale, font_thickness
            [320, 240, 1.3, 2],
            [640, 480, 1.3, 2],
        ]
        for config in configs:
            res = config[0:2]
            font_scale = config[2]
            font_thickness = config[3]
            img_res = self.get_img_copy(img, res)

            # warm up
            print("warn up")
            for i in range(self.warmup_times):
                hist = img_res.get_histogram()

            # item name
            item_name = f"hist gray {res[0]}x{res[1]}"

            # draw hint
            msg = f"{item_name} ..."
            print(msg)
            size = image.string_size(msg, scale=font_scale, thickness=font_thickness)
            img_disp = img_res.copy()
            img_disp.draw_rect(0, (img_disp.height() - size.height()) // 2 - 10, img_disp.width(), size.height() + 20, image.COLOR_RED, thickness=-1)
            img_disp.draw_string((img_disp.width() - size.width()) // 2, (img_disp.height() - size.height()) // 2, msg, image.COLOR_WHITE, scale=font_scale, thickness=font_thickness)

            # draw histogram on image left top
            bins = hist.bins()
            bin_max = max(bins)
            hist_show_w, hist_show_h = [img_disp.width() // 2, img_disp.height() // 2 - size.height()]
            bin_w = max(hist_show_w // len(bins), 1)
            hist_show_w = bin_w * len(bins)
            x = bin_w // 2
            img_disp.draw_rect(0, 0, hist_show_w, hist_show_h, image.COLOR_BLACK, thickness=-1)
            last = [x, int((1.0 - bins[0] / bin_max) * hist_show_h)]
            for b in bins[1:]:
                x += bin_w
                y = int((1.0 - b / bin_max) * hist_show_h)
                img_disp.draw_line(last[0], last[1], x, y, image.COLOR_WHITE, thickness=font_thickness)
                last = [x, y]
            self.disp.show(img_disp)

            # run
            t_sum = 0
            print(f"run {self.repeat_times} times")
            for i in range(self.repeat_times):
                t = time.ticks_us()
                hist = img_res.get_histogram()
                t_sum += time.ticks_us() - t
            t = t_sum / self.repeat_times / 1000
            fps = 1000 // t
            items[item_name] = f"{t:.1f} ms, {fps} fps"
            print(item_name, ":", items[item_name])
            del img_res, img_disp
            gc.collect()
            print("end one instance")

    def benchmark_openmv_qrcode(self, items):
        img0 = image.load("/maixapp/share/picture/2024.1.1/qrcode_640x480.jpg")
        configs = [
            # width, height, font_scale, font_thickness, use_NPU
            [320, 240, 1.3, 2, True],
            [640, 480, 2, 2, True],
            [640, 480, 2, 2, False]
        ]
        detector = image.QRCodeDetector()

        for config in configs:
            res = config[:2]
            font_scale = config[2]
            font_thickness = config[3]
            use_npu = config[4]
            img = self.get_img_copy(img0, res)

            # warm up
            print("warn up")
            for i in range(self.warmup_times):
                if use_npu:
                    qrcodes = detector.detect(img)
                else:
                    qrcodes = img.find_qrcodes()
            img_disp = img.copy()
            # item name
            item_name = f"qrcode {res[0]}x{res[1]} {'NPU' if config[4] else 'noNPU'}"
            # draw results
            for qrcode in qrcodes:
                corners = qrcode.corners()
                for i in range(4):
                    img_disp.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_GREEN, thickness=font_thickness)
                img_disp.draw_string(corners[0][0], corners[0][1] - 20, qrcode.payload(), image.COLOR_RED, scale=font_scale, thickness=font_thickness)
            # draw hint
            msg = f"{item_name} ..."
            print(msg)
            size = image.string_size(msg, scale=font_scale, thickness=font_thickness)
            img_disp.draw_rect(0, (img_disp.height() - size.height()) // 2 - 10, img_disp.width(), size.height() + 20, image.COLOR_RED, thickness=-1)
            img_disp.draw_string((img_disp.width() - size.width()) // 2, (img_disp.height() - size.height()) // 2, msg, image.COLOR_WHITE, scale=font_scale, thickness=font_thickness)
            self.disp.show(img_disp)

            # run
            t_sum = 0
            print(f"run {self.repeat_times} times")
            for i in range(self.repeat_times):
                if use_npu:
                    t = time.ticks_us()
                    qrcodes = detector.detect(img)
                    t_sum += time.ticks_us() - t
                else:
                    t = time.ticks_us()
                    qrcodes = img.find_qrcodes()
                    t_sum += time.ticks_us() - t
            t = t_sum / self.repeat_times / 1000  # ms
            fps = 1000 // t
            items[item_name] = f"{t:.1f} ms, {fps} fps"
            print(item_name, ":", items[item_name])
            del img, img_disp
            gc.collect()
            print("end one instance")

    def benchmark_opencv_binary(self, items):
        img_rgb = cv2.imread("/maixapp/share/picture/2024.1.1/cube_640x480.jpg")
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        ths = [0, 150]
        configs = [
            # width, height, font_scale, font_thickness
            [320, 240, 1.3, 2],
            [640, 480, 2, 2],
        ]
        for config in configs:
            res = config[0:2]
            font_scale = config[2]
            font_thickness = config[3]
            img_gray_copy = cv2.resize(img_gray, (res[0], res[1]))
            # warm up
            print("warn up")
            for i in range(self.warmup_times):
                img_disp = img_gray_copy.copy()
                img_disp = cv2.inRange(img_disp, ths[0], ths[1])
            # item name
            item_name = f"binary gray {res[0]}x{res[1]}"
            # draw hint
            msg = f"{item_name} ..."
            print(msg)
            size = cv2.getTextSize(msg, cv2.FONT_HERSHEY_PLAIN, font_scale, font_thickness)[0]
            img_disp = cv2.rectangle(img_disp, (0, (img_disp.shape[0] - size[1]) // 2 - 10), (img_disp.shape[1], (img_disp.shape[0] + size[1]) // 2 + 10), (0, 0, 255), thickness=-1)
            img_disp = cv2.putText(img_disp, msg, ((img_disp.shape[1] - size[0]) // 2, (img_disp.shape[0] + size[1]) // 2), cv2.FONT_HERSHEY_PLAIN, font_scale, (255, 255, 255), thickness=font_thickness)
            self.disp.show(image.cv2image(img_disp, True, False))

            # run
            t_sum = 0
            print(f"run {self.repeat_times} times")
            for i in range(self.repeat_times):
                img_disp = img_gray_copy.copy()
                t = time.ticks_us()
                img_disp = cv2.inRange(img_disp, ths[0], ths[1])
                t_sum += time.ticks_us() - t
            t = t_sum / self.repeat_times / 1000  # ms
            fps = 1000 // t
            items[item_name] = f"{t:.1f} ms, {fps} fps"
            print(item_name, ":", items[item_name])
            del img_gray_copy, img_disp
            gc.collect()
            print("end one instance")

    def benchmark_opencv_binary_adaptive(self, items):
        img_rgb = cv2.imread("/maixapp/share/picture/2024.1.1/cube_640x480.jpg")
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        configs = [
            # width, height, font_scale, font_thickness
            [320, 240, 1.3, 2],
            [640, 480, 2, 2],
        ]
        for config in configs:
            res = config[0:2]
            font_scale = config[2]
            font_thickness = config[3]
            img_gray_copy = cv2.resize(img_gray, (res[0], res[1]))
            # warm up
            print("warn up")
            for i in range(self.warmup_times):
                img_disp = img_gray_copy.copy()
                img_disp = cv2.adaptiveThreshold(img_disp, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
            # item name
            item_name = f"binary_adaptive gray {res[0]}x{res[1]}"
            # draw hint
            msg = f"{item_name} ..."
            print(msg)
            size = cv2.getTextSize(msg, cv2.FONT_HERSHEY_PLAIN, font_scale, font_thickness)[0]
            img_disp = cv2.rectangle(img_disp, (0, (img_disp.shape[0] - size[1]) // 2 - 10), (img_disp.shape[1], (img_disp.shape[0] + size[1]) // 2 + 10), (0, 0, 255), thickness=-1)
            img_disp = cv2.putText(img_disp, msg, ((img_disp.shape[1] - size[0]) // 2, (img_disp.shape[0] + size[1]) // 2), cv2.FONT_HERSHEY_PLAIN, font_scale, (255, 255, 255), thickness=font_thickness)
            self.disp.show(image.cv2image(img_disp, True, False))

            # run
            t_sum = 0
            print(f"run {self.repeat_times} times")
            for i in range(self.repeat_times):
                img_disp = img_gray_copy.copy()
                t = time.ticks_us()
                img_disp = cv2.adaptiveThreshold(img_disp, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
                t_sum += time.ticks_us() - t
            t = t_sum / self.repeat_times / 1000
            fps = 1000 // t
            items[item_name] = f"{t:.1f} ms, {fps} fps"
            print(item_name, ":", items[item_name])
            del img_gray_copy, img_disp
            gc.collect()
            print("end one instance")

    def benchmark_opencv_hist(self, items):
        img_rgb = cv2.imread("/maixapp/share/picture/2024.1.1/cube_640x480.jpg")
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        configs = [
            # width, height, font_scale, font_thickness
            [320, 240, 1.3, 2],
            [640, 480, 2, 2],
        ]
        for config in configs:
            res = config[0:2]
            font_scale = config[2]
            font_thickness = config[3]
            img_gray_copy = cv2.resize(img_gray, (res[0], res[1]))
            # warm up
            print("warn up")
            for i in range(self.warmup_times):
                hist = cv2.calcHist([img_gray_copy], [0], None, [256], [0, 256])
            # item name
            item_name = f"hist gray {res[0]}x{res[1]}"
            # draw hint
            msg = f"{item_name} ..."
            print(msg)
            size = cv2.getTextSize(msg, cv2.FONT_HERSHEY_PLAIN, font_scale, font_thickness)[0]
            img_disp = img_gray_copy.copy()
            img_disp = cv2.rectangle(img_disp, (0, (img_disp.shape[0] - size[1]) // 2 - 10), (img_disp.shape[1], (img_disp.shape[0] + size[1]) // 2 + 10), (0, 0, 255), thickness=-1)
            img_disp = cv2.putText(img_disp, msg, ((img_disp.shape[1] - size[0]) // 2, (img_disp.shape[0] + size[1]) // 2), cv2.FONT_HERSHEY_PLAIN, font_scale, (255, 255, 255), thickness=font_thickness)

            # draw histogram on image left top
            bins = hist.flatten() / hist.max()
            hist_show_w, hist_show_h = [img_disp.shape[1] // 2, img_disp.shape[0] // 2 - size[1]]
            bin_w = max(hist_show_w // len(bins), 1)
            hist_show_w = bin_w * len(bins)
            x = bin_w // 2
            img_disp = cv2.rectangle(img_disp, (0, 0), (hist_show_w, hist_show_h), (0, 0, 0), thickness=-1)
            last = (x, int((1.0 - bins[0]) * hist_show_h))
            for b in bins[1:]:
                x += bin_w
                y = int((1.0 - b) * hist_show_h)
                img_disp = cv2.line(img_disp, last, (x, y), (255, 255, 255), thickness=font_thickness)
                last = (x, y)
            self.disp.show(image.cv2image(img_disp, True, False))

            # run
            t_sum = 0
            print(f"run {self.repeat_times} times")
            for i in range(self.repeat_times):
                t = time.ticks_us()
                hist = cv2.calcHist([img_gray_copy], [0], None, [256], [0, 256])
                t_sum += time.ticks_us() - t
            t = t_sum / self.repeat_times / 1000
            fps = 1000 // t
            items[item_name] = f"{t:.1f} ms, {fps} fps"
            print(item_name, ":", items[item_name])
            del img_gray_copy, img_disp
            gc.collect()
            print("end one instance")

    def benchmark_opencv_findcontours(self, items):
        img_rgb = cv2.imread("/maixapp/share/picture/2024.1.1/rect_640x480.jpg")
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        img_binary = cv2.adaptiveThreshold(img_gray, 255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY_INV, 27, 31)
        configs = [
            # width, height, font_scale, font_thickness
            [320, 240, 1.3, 2],
            [640, 480, 2, 2],
        ]
        for config in configs:
            res = config[0:2]
            font_scale = config[2]
            font_thickness = config[3]
            img_binary_copy = cv2.resize(img_binary, (res[0], res[1]))
            img_rgb_copy = cv2.resize(img_rgb, (res[0], res[1]))

            # warm up
            print("warn up")
            for i in range(self.warmup_times):
                contours, _ = cv2.findContours(img_binary_copy, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # draw contours on image
            img_disp = img_rgb_copy.copy()
            for contour in contours:
                cv2.drawContours(img_disp, [contour], -1, (0, 255, 0), thickness=font_thickness)
            # item name
            item_name = f"find_contours {res[0]}x{res[1]}"
            # draw hint
            msg = f"{item_name} ..."
            print(msg)
            size = cv2.getTextSize(msg, cv2.FONT_HERSHEY_PLAIN, font_scale, font_thickness)[0]
            img_disp = cv2.rectangle(img_disp, (0, (img_disp.shape[0] - size[1]) // 2 - 10), (img_disp.shape[1], (img_disp.shape[0] + size[1]) // 2 + 10), (0, 0, 255), thickness=-1)
            img_disp = cv2.putText(img_disp, msg, ((img_disp.shape[1] - size[0]) // 2, (img_disp.shape[0] + size[1]) // 2), cv2.FONT_HERSHEY_PLAIN, font_scale, (255, 255, 255), thickness=font_thickness)
            self.disp.show(image.cv2image(img_disp, True, False))

            # run
            t_sum = 0
            print(f"run {self.repeat_times} times")
            for i in range(self.repeat_times):
                t = time.ticks_us()
                contours, _ = cv2.findContours(img_binary_copy, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                t_sum += time.ticks_us() - t
            t = t_sum / self.repeat_times / 1000
            fps = 1000 // t
            items[item_name] = f"{t:.1f} ms, {fps} fps"
            print(item_name, ":", items[item_name])
            del img_binary_copy, img_disp
            gc.collect()
            print("end one instance")


    def benchmark_openmv(self, items):
        self.benchmark_openmv_binary(items)
        self.benchmark_openmv_find_blobs(items)
        self.benchmark_openmv_hist(items)
        self.benchmark_openmv_qrcode(items)


    def benchmark_opencv(self, items):
        self.benchmark_opencv_binary(items)
        self.benchmark_opencv_binary_adaptive(items)
        self.benchmark_opencv_hist(items)
        self.benchmark_opencv_findcontours(items)

    def run(self):
        items = {
            "OpenMV": {},
            "OpenCV": {}
        }
        self.benchmark_openmv(items["OpenMV"])
        self.benchmark_opencv(items["OpenCV"])

        # show results
        if self.disp.height() > 480:
            font_scale = 2.3
            title_font_scale = 3
        elif self.disp.height() > 240:
            font_scale = 1.4
            title_font_scale = 2.1
        imgs = []
        for k, v in items.items():
            img = image.Image(self.disp.width(), self.disp.height(), bg=image.COLOR_BLACK)
            size = image.string_size("aA!~=?")
            y = 2
            ai_isp = int(app.get_sys_config_kv("npu", "ai_isp", "0"))
            img.draw_string(2, y , f"AI ISP: {'ON(model use part of NPU)' if ai_isp==1 else 'OFF(model use all NPU)'}", scale=font_scale + 0.2)
            y += int(size.height() * 1.2 + size.height() * 1.2 // 2)
            img.draw_string(2, y , f"{k}: avg {self.repeat_times} times", scale=font_scale + 0.2)
            y += int(size.height() * 1.2 + size.height() * 1.2 // 2)
            for k, v in v.items():
                img.draw_string(2, y , f"{k}: {v}", scale=font_scale)
                y += size.height() + size.height() // 2
            imgs.append(img)

        return True, imgs

if __name__ == "__main__":
    from maix import app

    disp = display.Display()
    obj = Bechmark(disp)
    img = obj.run()
    disp.show(img)
    while not app.need_exit():
        time.sleep_ms(10)
