---
title: MaixCAM MaixPy Face Detection and Keypoint Detection
---

## Introduction

Face detection can be applied in many scenarios, such as providing the face detection step for face recognition, or for face tracking applications, etc.

The face detection provided here can not only detect faces but also detect 5 key points, including two eyes, one nose, and two corners of the mouth.

![face detection](../../assets/face_detection.jpg)

## Using Face Detection in MaixPy

MaixPy officially provides three face detection models from the open-source projects [Face Detector 1MB with landmark](https://github.com/biubug6/Face-Detector-1MB-with-landmark), [Retinaface](https://github.com/biubug6/Pytorch_Retinaface), and [YOLOv8-face](https://github.com/derronqi/yolov8-face).

All three models can be used. `YOLOv8-face` performs better but is slightly slower, so you can choose based on your testing.

Using `YOLOv8-face` (requires MaixPy version >= 4.3.8):

```python
from maix import camera, display, image, nn, app

detector = nn.YOLOv8(model="/root/models/yolov8n_face.mud", dual_buff = True)

cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
disp = display.Display()

while not app.need_exit():
    img = cam.read()
    objs = detector.detect(img, conf_th = 0.5, iou_th = 0.45, keypoint_th = 0.5)
    for obj in objs:
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color = image.COLOR_RED)
        msg = f'{detector.labels[obj.class_id]}: {obj.score:.2f}'
        img.draw_string(obj.x, obj.y, msg, color = image.COLOR_RED)
        detector.draw_pose(img, obj.points, 2, image.COLOR_RED)
    disp.show(img)
```

For the other two models:
Here, a line of commented-out code is used to load the `Retinaface` model. Choose which line of code to use based on the model you download.

```python
from maix import camera, display, image, nn, app
import math

detector = nn.Retinaface(model="/root/models/retinaface.mud")
# detector = nn.FaceDetector(model="/root/models/face_detector.mud")

cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
disp = display.Display()

while not app.need_exit():
    img = cam.read()
    objs = detector.detect(img, conf_th = 0.4, iou_th = 0.45)
    for obj in objs:
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color = image.COLOR_RED)
        radius = math.ceil(obj.w / 10)
        img.draw_keypoints(obj.points, image.COLOR_RED, size = radius if radius < 5 else 4)
    disp.show(img)
```

## Model Downloads and Other Resolution Models

Download the models; the compressed package contains multiple resolutions to choose from. Higher resolution models are more accurate but take longer to process:
* [Face Detector 1MB with landmark](https://maixhub.com/model/zoo/377)
* [Retinaface](https://maixhub.com/model/zoo/378)
* [YOLOv8-face](https://maixhub.com/model/zoo/407)

## dual_buff Dual Buffer Acceleration

You may have noticed that the model initialization uses `dual_buff` (which defaults to `True`). Enabling the `dual_buff` parameter can improve running efficiency and increase the frame rate. For detailed principles and usage notes, see [dual_buff Introduction](./dual_buff.md).
