---
title: MaixCAM MaixPy 图像语义分割
---

## 简介

图像语义分割，就是识别图中特定的物体，并且讲物体部分的像素识别出来，比如下图识别到了人体和狗的身体部分，可以拿来做碰撞检测、汽车自动导航、面积测算等等。

![](../../assets/yolov8_seg.jpg)


## MaixPy 使用图像语义分割

MaixPy 默认提供了 coco 数据集 80 种物体分类模型。

> MaixPy 版本必须 >= 4.4.0

代码如下，也可以在 [MaixPy examples](https://github.com/sipeed/maixpy/tree/main/examples/) 中找到。

```python
from maix import camera, display, image, nn, app, time

detector = nn.YOLOv8(model="/root/models/yolov8n_seg.mud", dual_buff = True)

cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
dis = display.Display()

while not app.need_exit():
    img = cam.read()
    objs = detector.detect(img, conf_th = 0.5, iou_th = 0.45)
    for obj in objs:
        # img.draw_image(obj.x, obj.y, obj.seg_mask)
        detector.draw_seg_mask(img, obj.x, obj.y, obj.seg_mask, threshold=127)
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color = image.COLOR_RED)
        msg = f'{detector.labels[obj.class_id]}: {obj.score:.2f}'
        img.draw_string(obj.x, obj.y, msg, color = image.COLOR_RED)
    dis.show(img)
```

## 更多分辨率模型

默认是 320x224 输入分辨率的模型， 更多分辨率请到 [MaixHub 模型库](https://maixhub.com/model/zoo/413) 下载。

## dual_buff 双缓冲区加速

你可能注意到这里模型初始化使用了`dual_buff`（默认值就是 `True`），使能 `dual_buff` 参数可以加快运行效率，提高帧率，具体原理和使用注意点见 [dual_buff 介绍](./dual_buff.md)。


## 自定义自己的物体分割模型

上面提供的是 coco 数据集 80 分类的模型，如果不满足你的要求，你也可以自己训练特定的物体检测和分割模型，按照 [离线训练YOLOv8](./customize_model_yolov8.md) 所述使用 YOLOv8 官方的分格模型训练方法进行训练，然后转换成 MaixCAM 支持的模型格式即可。

