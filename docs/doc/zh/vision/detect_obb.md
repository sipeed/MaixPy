---
tite: 带旋转角度的目标检测(OBB, Oriented Bounding Box)
update:
    - date: 2024-12-20
      version: v1.0
      author: neucrack
      content:
        支持 YOLO11/YOLOv8 OBB 模型并添加文档
---

## 简介

普通的检测中输出结果是一个矩形框，但是在一些场景中，目标物体的形状是旋转的，这时候就需要输出一个带旋转角度的矩形框，这种矩形框叫做OBB(Oriented Bounding Box)。
![](../../assets/ships-detection-using-obb.jpeg)

普通检测结果： x, y, w, h, 分别是 矩形框左上角或者中心点坐标，以及矩形宽高。
OBB 检测结果：x, y, w, h, angle, 多了一个旋转角度。

## MaixPy MaixCAM 中使用带旋转角度的目标检测(OBB)

`MaixPy` 中移植了 `YOLO11/YOLOv8` `OBB` 模型，可以快速方便地实现， 以下为例程，以[MaixPy/examples](https://github.com/sipeed/maixpy)中的`nn_yolo11_obb.py`为准：
```python
from maix import camera, display, image, nn, app

detector = nn.YOLO11(model="/root/models/yolo11n_obb.mud", dual_buff = True)

cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
disp = display.Display()

while not app.need_exit():
    img = cam.read()
    objs = detector.detect(img, conf_th = 0.5, iou_th = 0.45)
    for obj in objs:
        points = obj.get_obb_points()
        msg = f'{detector.labels[obj.class_id]}: {obj.score:.2f}, {obj.angle * 180:.1f}'
        img.draw_string(points[0], points[1] - 4, msg, color = image.COLOR_RED)
        detector.draw_pose(img, points, 8 if detector.input_width() > 480 else 4, image.COLOR_RED, close=True)
    disp.show(img)
```

可以看到这里使用`YOLO11`加载了`obb`模型，然后在检测到目标后，通过`obj.angle`获取到矩形旋转角度，`obj`的`x,y,w,h`属性是未旋转的矩形，通过`get_obb_points`获取到旋转后的矩形的四个顶点坐标，然后通过`draw_pose`绘制出目标的旋转矩形框，`close`参数表示将矩形框四个顶点连线起来。


默认的模型是 YOLO11 官方的`15`类模型，分类标签如下：
```python
plane, ship, storage tank, baseball diamond, tennis court, basketball court, ground track field, harbor, bridge, large vehicle, small vehicle, helicopter, roundabout, soccer ball field, swimming pool
```
在`/root/models/yolo11n_obb.mud`文件中也能看到。

## 更多输入分辨率

默认的输入图像分辨率是`320x224`，如果需要更高的分辨率，可以到[MaixHub 模型库](https://maixhub.com/model/zoo/869) 下载，或者按照后文自定义模型。

## MaixPy MaixCAM 自定义自己的OBB模型

### 电脑端使用模型

关于 `YOLO11` 官方的 OBB 模型介绍请看[YOLO11 OBB](https://docs.ultralytics.com/tasks/obb/)。
在这个文档中可以看到如何在电脑端使用`obb`模型，以及如何导出 ONNX 模型文件。

### 导出模型给 MaixCAM 使用

根据 [YOLO11/YOLOv8 自定义模型](./customize_model_yolov8.md) 即可将 ONNX 模型转换为 MaixCAM 可以使用的 MUD 模型。
注意：转换时需要注意输出层的输出名不要弄错。

### 训练自己的 OBB 模型

根据[YOLO11 官方训练文档](https://docs.ultralytics.com/datasets/obb/dota-v2/) 准备自己的数据集，然后进行训练即可。




