

from maix import image, time, display, touchscreen, nn, tensor, app, sys
import gc
import os
import numpy as np

class Bechmark:
    name = "NPU"

    def __init__(self):
        self.warmup_times = 3
        self.repeat_times = 40
        self.disp = display.Display()
        self.ts = touchscreen.TouchScreen()

    def benchmark_yolo_detect_img(self, items):
        test_items = []
        path_11n = "/root/models/yolo11n.mud"
        path_11s = "/root/models/yolo11s.mud"
        path_5s = "/root/models/yolov5s.mud"
        path_11n_640 = "/root/models/yolo11n_640.mud"
        path_11s_640 = "/root/models/yolo11s_640.mud"
        path_11l_640 = "/root/models/yolo11l_640.mud"
        test_items.append((path_11n, nn.YOLO11, False))
        if os.path.exists(path_11s):
            test_items.append((path_11s, nn.YOLO11, False))
        test_items.append((path_5s, nn.YOLOv5, False))
        if os.path.exists(path_11n_640):
            test_items.append((path_11n_640, nn.YOLO11, False))
        if os.path.exists(path_11s_640):
            test_items.append((path_11s_640, nn.YOLO11, False))
        if os.path.exists(path_11l_640):
            test_items.append((path_11l_640, nn.YOLO11, False))
        test_items.append((path_11n, nn.YOLO11, True))
        if os.path.exists(path_11s):
            test_items.append((path_11s, nn.YOLO11, True))
        test_items.append((path_5s, nn.YOLOv5, True))
        if os.path.exists(path_11n_640):
            test_items.append((path_11n_640, nn.YOLO11, True))
        if os.path.exists(path_11s_640):
            test_items.append((path_11s_640, nn.YOLO11, True))
        if os.path.exists(path_11l_640):
            test_items.append((path_11l_640, nn.YOLO11, True))

        for (model_path, _class, dual_buff) in test_items:
            print(model_path, _class, dual_buff)
            yolo = _class(model_path, dual_buff=dual_buff)
            img = image.load("/maixapp/share/picture/2024.1.1/test_coco_640.jpg").resize(yolo.input_width(), yolo.input_height(), image.Fit.FIT_COVER)
            # item name
            name = os.path.splitext(os.path.basename(model_path))[0]
            item_name = f"{name} {yolo.input_width()}x{yolo.input_height()} {'dual_buff' if dual_buff else ''}"
            # show hint
            msg = f"{item_name} ..."
            print(msg)
            scale = (4 if img.height() >= 1080 else 2) if img.height() >= 480 else 1
            thickness = (4 if img.height() >= 1080 else 2) if img.height() >= 480 else 1
            size = image.string_size(msg, scale = scale, thickness=thickness)
            img.draw_rect(0, (img.height() - size.height()) // 2 - 10, img.width(), size.height() + 20, image.COLOR_RED, thickness=-1)
            img.draw_string((img.width() - size.width()) // 2, (img.height() - size.height()) // 2, msg, image.COLOR_WHITE, scale = scale, thickness=thickness)
            self.disp.show(img)

            # warm up
            print("warn up")
            for i in range(self.warmup_times):
                yolo.detect(img, conf_th = 0.5, iou_th = 0.45)
            t_sum = 0
            print(f"run {self.repeat_times} times")
            for i in range(self.repeat_times):
                t = time.ticks_us()
                yolo.detect(img, conf_th = 0.5, iou_th = 0.45)
                t_sum += time.ticks_us() - t
            t = t_sum / self.repeat_times
            fps = 1000000 // t
            items[item_name] = f"{t/1000:.1f} ms, {fps} fps"
            print(item_name, ":", items[item_name])
            if dual_buff: # wait for last time detect complete then del yolo
                start_t = time.ticks_ms()
                while time.ticks_ms() - start_t <= t / 1000:
                    time.sleep_ms(2)
            del yolo
            gc.collect()
            print("end one instance")


    def benchmark_forward_img(self, items):
        test_items = []
        path_11n = "/root/models/yolo11n.mud"
        path_11s = "/root/models/yolo11s.mud"
        path_11n_640 = "/root/models/yolo11n_640.mud"
        path_11s_640 = "/root/models/yolo11s_640.mud"
        path_11l_640 = "/root/models/yolo11l_640.mud"
        path_5s = "/root/models/yolov5s.mud"
        path_mbn = "/root/models/mobilenetv2.mud"
        detect_img = "/maixapp/share/picture/2024.1.1/test_coco_640.jpg"
        clssify_img = "/maixapp/share/picture/2024.1.1/cat.jpg"
        test_items.append((path_11n, detect_img))
        if os.path.exists(path_11s):
            test_items.append((path_11s, detect_img))
        if os.path.exists(path_11n_640):
            test_items.append((path_11n_640, detect_img))
        if os.path.exists(path_11s_640):
            test_items.append((path_11s_640, detect_img))
        if os.path.exists(path_11l_640):
            test_items.append((path_11l_640, detect_img))
        test_items.append((path_5s, detect_img))
        test_items.append((path_mbn, clssify_img))

        for (model_path, img_path) in test_items:
            model = nn.NN(model_path, dual_buff = False)
            layer_info = model.inputs_info()[0]
            chw = False
            if layer_info.shape[1] < 4:
                w = layer_info.shape[3]
                h = layer_info.shape[2]
                chw = True
            else:
                w = layer_info.shape[2]
                h = layer_info.shape[1] 
            img = image.load(img_path).resize(w, h, image.Fit.FIT_COVER)
            # item name
            name = os.path.splitext(os.path.basename(model_path))[0]
            item_name = f"{name} {w}x{h}"
            # show hint
            msg = f"{item_name} ..."
            print(msg)
            scale = (4 if img.height() >= 1080 else 2) if img.height() >= 480 else 1
            thickness = (4 if img.height() >= 1080 else 2) if img.height() >= 480 else 1
            size = image.string_size(msg, scale = scale, thickness=thickness)
            img_disp = img.copy()
            img_disp.draw_rect(0, (img.height() - size.height()) // 2 - 10, img.width(), size.height() + 20, image.COLOR_RED, thickness=-1)
            img_disp.draw_string((img.width() - size.width()) // 2, (img.height() - size.height()) // 2, msg, image.COLOR_WHITE, scale = scale, thickness=thickness)
            self.disp.show(img_disp)
            del img_disp
            input_tensors = tensor.Tensors()
            if sys.device_id() in ["maixcam", "maixcam_pro"] or layer_info.dtype == tensor.DType.FLOAT32: # not integrated preprocess
                print("preprocess")
                img_array = image.image2cv(img, copy=False)
                img_array = img_array.astype("float32")
                mean = model.extra_info().get("mean", "0")
                scale = model.extra_info().get("scale", "1")
                mean = list(map(float, mean.split(",")))
                scale = list(map(float, scale.split(",")))
                img_array = (img_array - np.array(mean, dtype="float32")) * np.array(scale, dtype="float32")
                if layer_info.layout == nn.Layout.NCHW:
                    img_array = np.transpose(img_array, (2, 0, 1))
                input_tensor = tensor.tensor_from_numpy_float32(img_array, copy = False)
            else:
                print("already integraged preprocess")
                input_tensor = img.to_tensor(chw=chw, copy=False)
            input_tensor.expand_dims(0)
            input_tensors.add_tensor(layer_info.name, input_tensor, copy = False, auto_delete = False)

            # warm up
            for i in range(self.warmup_times):
                # model.forward_image(img)
                model.forward(input_tensors, copy_result = False)
            t_sum = 0
            for i in range(self.repeat_times):
                t = time.ticks_us()
                # model.forward_image(img)
                model.forward(input_tensors, copy_result = False)
                t_sum += time.ticks_us() - t
            del model
            gc.collect()
            t = t_sum / self.repeat_times
            fps = 1000000 // t
            items[item_name] = f"{t/1000:.1f} ms, {fps} fps"
            print(item_name, ":", items[item_name])

    def run(self):
        items = {
            "Detect": {},
            "Forward": {}
        }
        self.benchmark_yolo_detect_img(items["Detect"])
        self.benchmark_forward_img(items["Forward"])

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
