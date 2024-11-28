---
title: Introduction to Running Models in Dual Buffer Mode with MaixPy MaixCAM
---

## Introduction

You may have noticed that there is a parameter `dual_buff=True` when initializing the code for model running. For example, in `YOLOv5`:

```python
from maix import camera, display, image, nn, app

detector = nn.YOLOv5(model="/root/models/yolov5s.mud", dual_buff=True)
# detector = nn.YOLOv8(model="/root/models/yolov8n.mud", dual_buff=True)

cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
disp = display.Display()

while not app.need_exit():
    img = cam.read()
    objs = detector.detect(img, conf_th = 0.5, iou_th = 0.45)
    for obj in objs:
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color = image.COLOR_RED)
        msg = f'{detector.labels[obj.class_id]}: {obj.score:.2f}'
        img.draw_string(obj.x, obj.y, msg, color = image.COLOR_RED)
    disp.show(img)
```

Generally, this parameter defaults to `True`, unless you manually set `dual_buff=False` to disable the dual buffer function.

Enabling this feature improves running efficiency, thereby increasing the frame rate (assuming the camera's frame rate is not limited, the above code will halve the loop time on MaixCAM, effectively doubling the frame rate). However, there are drawbacks. The `detect` function returns the result of the previous call to the `detect` function, meaning there is a one-frame delay between the result and the input. If you want the detection result to match the input `img` rather than the previous frame, disable this feature. Additionally, due to the preparation of dual buffers, memory usage will increase. If you encounter insufficient memory issues, you will also need to disable this feature.

## Principle

Model object detection involves several steps:

* Capturing the image
* Image preprocessing
* Model execution
* Post-processing the results

Only the model execution step runs on the hardware NPU, while other steps run on the CPU.

If `dual_buff` is set to `False`, during `detect`, the CPU preprocesses (while the NPU is idle), then the NPU performs the computation (while the CPU is idle waiting for the NPU to finish), and then the CPU post-processes (while the NPU is idle). This process is linear and relatively simple. However, a problem arises because either the CPU or the NPU is always idle. When `dual_buff=True` is enabled, the CPU preprocesses and hands off to the NPU for computation. At this point, the CPU does not wait for the NPU to produce results but instead exits the `detect` function and proceeds to the next camera read and preprocess. Once the NPU finishes its computation, the CPU has already prepared the next data, immediately passing it to the NPU to continue computing without giving the NPU any idle time. This maximizes the efficient simultaneous operation of both the CPU and NPU.

However, note that if the camera frame rate is not high enough, it will still limit the overall frame rate.

