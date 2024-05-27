---
title: MaixPy Face Detection and Key Points Detection
---

## Introduction

Face detection can be used in many places, such as providing the step of face detection for face recognition, or applications related to face tracking, and more.

The face detection provided here can not only detect faces but also detect 5 key points, including two eyes, one nose, and the two corners of a mouth.

![face detection](../../assets/face_detection.jpg)

## Using Face Detection in MaixPy

MaixPy officially provides two face detection models, sourced from the open projects [face detector 1MB with landmark](https://github.com/biubug6/Face-Detector-1MB-with-landmark) and [Retinaface](https://github.com/biubug6/Pytorch_Retinaface).

To use them, first download a model, either one as there's not much difference between them:
* [face detector 1MB with landmark](https://maixhub.com/model/zoo/377)
* [Retinaface](https://maixhub.com/model/zoo/378)

Then copy the model file to your device, see [Using MaixVision](../basic/maixvision.md) for how to copy.
> The default image contains a file that can be used directly; if not available, you must download it yourself. The downloaded zip package contains multiple resolutions to choose from; the higher the resolution, the more precise but also more time-consuming.

Next, run the code. The following line of commented code is for loading the `Retinaface` model, choose which line of code to use based on the model you downloaded.

> To use this function, MaixPy must >= 4.1.4.

```python
from maix import camera, display, image, nn, app
import math

detector = nn.Retinaface(model="/root/models/retinaface.mud")
# detector = nn.FaceDetector(model="/root/models/face_detector.mud")

cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
dis = display.Display()

while not app.need_exit():
    img = cam.read()
    objs = detector.detect(img, conf_th = 0.4, iou_th = 0.45)
    for obj in objs:
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color = image.COLOR_RED)
        radius = math.ceil(obj.w / 10)
        img.draw_keypoints(obj.points, image.COLOR_RED, size = radius if radius < 5 else 4)
    dis.show(img)

```
