---
title: MaixPy 使用 YOLOv5 模型进行目标检测
---


## 目标检测概念

目标检测是指在图像或视频中检测出目标的位置和类别，比如在一张图中检测出苹果、飞机等物体，并且标出物体的位置。

和分类不同的是多了一个位置信息，所以目标检测的结果一般是一个矩形框，框出物体的位置。

## MaixPy 中使用目标检测

MaixPy 默认提供了 `YOLOv5` 模型，可以直接使用：

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

效果视频:

<video playsinline controls autoplay loop muted preload src="https://wiki.sipeed.com/maixpy/static/video/detector.mp4" type="video/mp4">


这里使用了摄像头拍摄图像，然后传给 `detector`进行检测，得出结果后，将结果(分类名称和位置)显示在屏幕上。

更多 API 使用参考 [maix.nn](/api/maix/nn.html) 模块的文档。

## 训练自己的目标检测模型

请到[MaixHub](https://maixhub.com) 学习并训练目标检测模型，创建项目时选择`目标检测模型`即可。

