from maix import nn, app, time, image, tensor, sys
import os
import sys as py_sys
from collections import deque
import numpy as np

def main():
    model_fps = 0
    model_path = "/root/models/yolo11s.mud"
    if not os.path.exists(model_path):
        model_path = "/root/models/yolo11n.mud"
    print("stress_process start")
    # detector = nn.YOLO11(model=model_path, dual_buff = True)
    model = nn.NN(model_path, dual_buff = True)
    print("stress_process load model ok")
    img_path = "/maixapp/share/picture/2024.1.1/test_coco_640.jpg"
    if not os.path.exists(img_path):
        print(f"Image {img_path} not found!!!, exit")
        return -1
    print("stress_process load image", img_path)
    img = image.load(img_path)
    print("stress_process load image ok")
    layer_info = model.inputs_info()[0]
    chw = False
    if layer_info.shape[1] < 4:
        w = layer_info.shape[3]
        h = layer_info.shape[2]
        chw = True
    else:
        w = layer_info.shape[2]
        h = layer_info.shape[1] 
    img = img.resize(w, h, image.Fit.FIT_COVER)
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

    print("stress_process resize image ok")
    fps_window = deque(maxlen=30)
    err_count = 0
    last_err_time = 0
    last_print_time = 0
    while not app.need_exit():
        try:
            t = time.ticks_us()
            # objs = detector.detect(img, conf_th = 0.5, iou_th = 0.45)
            model.forward(input_tensors, copy_result = False)
            fps_window.append(time.ticks_us() - t)
            model_fps = fps_now = int(1000000 / (sum(fps_window) / len(fps_window)))
            if time.ticks_s() - last_err_time > 20:
                err_count = 0
            if time.ticks_ms() - last_print_time >= 1000:
                last_print_time = time.ticks_ms()
                print(f"[running result] fps: {model_fps}")
        except Exception as e:
            last_err_time = time.ticks_s()
            print("stress_process error occurrs")
            err_count += 1
            if err_count > 5:
                raise e
    print("stress_process exit")
    return 0

if __name__ == "__main__":
    py_sys.exit(main())
