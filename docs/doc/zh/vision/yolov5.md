---
title: MaixPy MaixCAM 使用 YOLOv5 / YOLOv8 / YOLO11 模型进行目标检测
---


## 目标检测概念

目标检测是指在图像或视频中检测出目标的位置和类别，比如在一张图中检测出苹果、飞机等物体，并且标出物体的位置。

和分类不同的是多了一个位置信息，所以目标检测的结果一般是一个矩形框，框出物体的位置。

## MaixPy 中使用目标检测

MaixPy 默认提供了 `YOLOv5` 和 `YOLOv8` 和 `YOLO11` 模型，可以直接使用：
> YOLOv8 需要 MaixPy >= 4.3.0。
> YOLO11 需要 MaixPy >= 4.7.0。

```python
from maix import camera, display, image, nn, app

detector = nn.YOLOv5(model="/root/models/yolov5s.mud", dual_buff=True)
# detector = nn.YOLOv8(model="/root/models/yolov8n.mud", dual_buff=True)
# detector = nn.YOLO11(model="/root/models/yolo11n.mud", dual_buff=True)

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

效果视频:

<div>
<video playsinline controls autoplay loop muted preload src="/static/video/detector.mp4" type="video/mp4">
</div>

这里使用了摄像头拍摄图像，然后传给 `detector`进行检测，得出结果后，将结果(分类名称和位置)显示在屏幕上。

以及这里 替换`YOLO11` 和 `YOLOv5` 和`YOLOv8`即可实现`YOLO11/v5/v8/`切换，注意模型文件路径也要修改。

模型支持的 80 种物体列表请看本文附录。

更多 API 使用参考 [maix.nn](/api/maix/nn.html) 模块的文档。

## dual_buff 双缓冲区加速

你可能注意到这里模型初始化使用了`dual_buff`（默认值就是 `True`），使能 `dual_buff` 参数可以加快运行效率，提高帧率，具体原理和使用注意点见 [dual_buff 介绍](./dual_buff.md)。


## 更多输入分辨率

默认的模型输入是`320x224`分辨率，因为这个分辨率比例和默认提供的屏幕分辨率接近，你也可以手动下载其它分辨率的模型替换：

YOLOv5: [https://maixhub.com/model/zoo/365](https://maixhub.com/model/zoo/365)
YOLOv8: [https://maixhub.com/model/zoo/400](https://maixhub.com/model/zoo/400)
YOLO11: [https://maixhub.com/model/zoo/453](https://maixhub.com/model/zoo/453)

分辨率越大精度越高，但是运行耗时越长，根据你的应用场景选择合适的即可。

## YOLOv5 和 YOLOv8 和 YOLO11 用哪个？

这里提供的 `YOLOv5s` 和 `YOLOv8n` 和 `YOLO11n` 三种模型，`YOLOv5s`模型更大，`YOLOv8n YOLO11n`速度快一点点， 精度按照官方数据来说`YOLO11n > YOLOv8n > YOLOv5s`，可以实际测试根据自己的实际情况选择。

另外你也可以尝试`YOLOv8s`或者`YOLO11s`，帧率会低一些（比如 yolov8s_320x224 比 yolov8n_320x224 慢 10ms），准确率会比前两个都高，模型可以在上面提到的模型库下载到或者自己从`YOLO`官方仓库导出模型。

## 摄像头分辨率和模型分辨率不同可以吗

上面使用`detector.detect(img)`函数进行检测时，如果 `img` 的分辨率和模型分辨率不同，这个函数内部会自动调用`img.resize`将图像缩放成和模型输入分辨率相同的，`resize`默认使用`image.Fit.FIT_CONTAIN` 方法，即保持宽高比缩放，周围填充黑色的方式，检测到的坐标也会自动映射到原`img`的坐标上。


## MaixHub 在线训练自己的目标检测模型

默认提供的 80 分类检测模型，如果你需要检测特定的物体，请到[MaixHub](https://maixhub.com) 学习并训练目标检测模型，创建项目时选择`目标检测模型`即可，参考[MaixHub 在线训练文档](./maixhub_train.md)。

或者到[MaixHub 模型库](https://maixhub.com/model/zoo?platform=maixcam) 找社区成员分享的模型。

## 离线训练自己的目标检测模型

强烈建议先使用 MaixHub 在线训练模型，此种方式难度比较大，不建议新手一来就碰这个方式。
此种方式有些许默认你知道的知识文中不会提，遇到问题多上网搜索学习。
请看 [离线训练YOLOv5模型](./customize_model_yolov5.md) 或者 [离线训练 YOLOv8/YOLO11 模型](./customize_model_yolov8.md)


## 附录：80分类

COCO 数据集的 8 种物体分别为：

```txt
person
bicycle
car
motorcycle
airplane
bus
train
truck
boat
traffic light
fire hydrant
stop sign
parking meter
bench
bird
cat
dog
horse
sheep
cow
elephant
bear
zebra
giraffe
backpack
umbrella
handbag
tie
suitcase
frisbee
skis
snowboard
sports ball
kite
baseball bat
baseball glove
skateboard
surfboard
tennis racket
bottle
wine glass
cup
fork
knife
spoon
bowl
banana
apple
sandwich
orange
broccoli
carrot
hot dog
pizza
donut
cake
chair
couch
potted plant
bed
dining table
toilet
tv
laptop
mouse
remote
keyboard
cell phone
microwave
oven
toaster
sink
refrigerator
book
clock
vase
scissors
teddy bear
hair drier
toothbrush
```