---
title: MaixCAM MaixPy MaixCAM 模型运行 dual_buff 模式介绍
---

## 简介

细心的你可能注意到模型运行相关的的代码初始化时有一个参数`dual_buff=True`。
比如 `YOLOv5`：
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

一般来说这个参数默认就是`True`，除非手动设置`dual_buff=False`才会关闭 `dual_buff`功能。

使能这个功能后运行的效率会提升，即帧率会提升（以上代码假设摄像头的帧率没有限制的情况下，在 MaixCAM 上会减少循环一半的时间即帧率翻倍）。
但是也有缺点，`detect`函数返回的结果是上一次调用`detect`函数的图的结果，所以结果和输入会有一帧的时间差，如果你希望`detect`出来的结果就是输入的`img`的结果而不是上一帧的结果，请禁用这个功能；另外由于准备了双份缓冲区，也会加大内存的使用，如果使用时发现内存不足，也需要禁用这个功能。


## 原理

模型检测物体分为了几步：
* 获取图像
* 图像预处理
* 模型运行
* 结果后处理

其中只有 模型运行这一步是硬件NPU 上运行的，其它步骤都在 CPU 运行。

如果`dual_buff`设置为`False`，在`detect`的时候，CPU 先预处理（此时 NPU 空闲）， 然后给 NPU 运算（此时 CPU 空闲等待 NPU 运算结束），然后 CPU 后处理（NPU 空闲）， 整过过程是线性的，比较简单。
但是这里发现了问题，就是 CPU 和 NPU 两者总有一个空闲着的，当加了`dual_buff=True`， CPU 预处理后交给 NPU 运算，此时 CPU 不再等待 NPU 出结果，二是直接退出`detect`函数进行下一次摄像头读取和预处理，等 NPU 运算完成后， CPU 已经准备好了下一次的数据直接交给 NPU 继续运算，不给 NPU 喘息的机会，这样就充分利用了 CPU 和 NPU 高效地同时进行运算。


不过这里也需要注意，摄像头帧率如果不够高也会限制整体帧率。



