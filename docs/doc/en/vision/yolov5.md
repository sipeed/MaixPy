---
title: Using YOLOv5 Model for Object Detection with MaixPy
---

## Concept of Object Detection

Object detection refers to identifying the position and category of targets in an image or video, such as detecting objects like apples and airplanes in a picture, and marking the position of these objects.

Unlike classification, object detection includes positional information, so the result is usually a rectangular box that frames the location of the object.

## Using Object Detection in MaixPy

MaixPy comes with the `YOLOv5` model by default, which can be used directly:

```python
from maix import camera, display, image, nn, app

detector = nn.YOLOv5(model="/root/models/yolov5s.mud")

cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
dis = display.Display()

while not app.need_exit():
    img = cam.read()
    objs = detector.detect(img, conf_th = 0.5, iou_th = 0.45)
    for obj in objs:
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color = image.COLOR_RED)
        msg = f'{detector.labels[obj.class_id]}: {obj.score:.2f}'
        img.draw_string(obj.x, obj.y, msg, color = image.COLOR_RED)
    dis.show(img)
```

Demonstration video:

<video playsinline controls autoplay loop muted preload src="https://wiki.sipeed.com/maixpy/static/video/detector.mp4" type="video/mp4">

This setup uses a camera to capture images, which are then sent to the `detector` for detection. The results (classification name and position) are displayed on the screen.

For more API usage, refer to the documentation of the [maix.nn](/api/maix/nn.html) module.

## Training Your Own Object Detection Model

Please visit [MaixHub](https://maixhub.com) to learn and train object detection models. When creating a project, select `Object Detection Model`.
