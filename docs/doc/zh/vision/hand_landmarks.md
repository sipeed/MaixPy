---
title: MaixPy MaixCAM 人手部 21 个关键点三维坐标检测
update:
    - date: 2024-12-31
      version: v1.0
      author: neucrack
      content:
        添加源码、模型、例程和文档
---


## 简介

在一些应用中我们需要检测手的位置，或者手的姿态时，可以使用本算法，此算法可以检测到：
* 手的位置，提供四个顶点坐标。
* 手的 21 个关键点坐标，以及每个点相对手掌的深度估计。

应用举例：
* 点读机
* 手势控制
* 手指类游戏
* 手语转译
* 施魔法

效果图如下：

<img src="../../assets/hands_landmarks.jpg" style="max-height:24rem">

效果视频：
<video playsinline controls autoplay loop muted preload src="/static/video/hands_landmarks.mp4" type="video/mp4">
Classifier Result video
</video>

21 个关键点包括：
![](../../assets/hand_landmarks_doc.jpg)


## MaixPy MaixCAM 中使用手关键点检测

在 **MaixPy** 中已经内置了该算法(移植于 mediapipe，有兴趣可自行学习)，可以方便地使用（**固件版本必须 >= 4.9.3**)，此例程也可以在[MaixPy/examples](https://github.com/sipeed/maixpy)目录中找到：
```python
from maix import camera, display, image, nn, app

detector = nn.HandLandmarks(model="/root/models/hand_landmarks.mud")
# detector = nn.HandLandmarks(model="/root/models/hand_landmarks_bf16.mud")
landmarks_rel = False

cam = camera.Camera(320, 224, detector.input_format())
disp = display.Display()

while not app.need_exit():
    img = cam.read()
    objs = detector.detect(img, conf_th = 0.7, iou_th = 0.45, conf_th2 = 0.8, landmarks_rel = landmarks_rel)
    for obj in objs:
        # img.draw_rect(obj.x, obj.y, obj.w, obj.h, color = image.COLOR_RED)
        msg = f'{detector.labels[obj.class_id]}: {obj.score:.2f}'
        img.draw_string(obj.points[0], obj.points[1], msg, color = image.COLOR_RED if obj.class_id == 0 else image.COLOR_GREEN, scale = 1.4, thickness = 2)
        detector.draw_hand(img, obj.class_id, obj.points, 4, 10, box=True)
        if landmarks_rel:
            img.draw_rect(0, 0, detector.input_width(detect=False), detector.input_height(detect=False), color = image.COLOR_YELLOW)
            for i in range(21):
                x = obj.points[8 + 21*3 + i * 2]
                y = obj.points[8 + 21** + i * 2 + 1]
                img.draw_circle(x, y, 3, color = image.COLOR_YELLOW)
    disp.show(img)
```

检测的结果用了`draw_hand`这个函数来画，你可以从`obj.points`得到所有关键点信息，一共`4 + 21`个点，格式为：
* 前 4 个点是手外框的四个角坐标，从左上角开始，逆时针4个点，`topleft_x, topleft_y, topright_x, topright_y, bottomright_x, bottomright_y， bottomleft_x, bottomleft_y`，注意值可能会小于0.
* 后 21 个点是手部的关键点，如简介中所说的顺序，格式：`x0, y0, z0, x1, y1, z1, ..., x20, y20, z20`，其中 `z`为相对于手掌的深度信息。注意值可能会小于 0。

另外`obj`的`x, y, w, h, angle` 属性也可以直接使用，分别代表了旋转前的框坐标和大小，以及旋转角度（0到360度）。

**精度优化**：这里使用了`nn.HandLandmarks`这个类来进行检测，默认用了`int8`量化的模型，速度会更快，如果需要更高的精度可以更换为`hand_landmarks_bf16.mud`这个模型。
**得到相对于手左上角顶点的关键点坐标**：你可以选择得到相对于手左上角顶点的关键点坐标值，值范围为 `0` 到 手框宽度(`obj.w`)，方法：
```python
objs = detector.detect(img, conf_th = 0.7, iou_th = 0.45, conf_th2 = 0.8, landmarks_rel = True)
```
这里`landmarks_rel` 参数就是告诉这个函数输出`21`个点相对于手左上角顶点的相对坐标，在`obj.points`最后`21x2`个值`x0y0x1y1..x20y20`排列。

## 进阶：基于关键点检测实现手姿态识别

举个例子，比如我们要实现检测石头剪刀布检测，有两种方法：
* 方法1： 直接根据关键点进行判断，使用代码判断手的形状，比如手指张开，手掌朝上，手掌朝下等等。
* 方法2： 使用 AI 模型进行分类。

方法1是传统的方法，简单快速，在简单的手势判断比较稳定，这里主要说`方法2`:
方法2 即用训练一个分类模型来对手势分类，不过可能需要大量图片和背景来训练，我们在此有两个优化方案：
1. 使用检测手的模型比如 YOLO11 先检测手，再裁切出只有手的部分，再训练分类模型，这样分类模型的输入只有手部分，减少了干扰。
2. 使用手关键点检测，得到关键点数据，用这 21 个关键点数据作为分类模型的输入进行分类，这样直接没有了背景信息，更加准确！

所以这里主要采用的就是思路 `2`，将关键点信息作为分类模型的输入，因为没有图片背景信息干扰，只需要采集比较少量的数据就能达到比较好的效果。
步骤：
* 确定分类的手势，比如石头剪刀布三个分类。
* 修改上面的代码，比如点击屏幕一下就记录下当前手的关键点信息到文件系统存起来。
* 修改上面的代码，为了让分类模型输入更统一，你可以选择得到相对于手左上顶点的关键点坐标值，值范围为 `0` 到 手框宽度(`obj.w`)，参考上面`landmarks_rel`参数。
* 分别采集这几个分类的数据。
* 在电脑上创建一个分类模型，比如基于 mobilenetv2 的分类模型，使用 pytorch 进行训练，实际输入还可以将坐标都归一化到[0, 1]。
* 分类模型训练完成后[导出成 MaixCAM 支持的格式](../ai_model_converter/maixcam.md)（量化数据需要先打包成`npz`格式）。
* 在 MaixPy 中检测手之后，得到关键点再运行分类模型进行得到结果，代码可以参考例程中的`nn_forward.py` 和 `nn_custom_classifier.py`。

这样就可以以很少的训练数据训练不同手势了，这种方式要求你会训练分类模型，以及量化转换模型格式。

## 进阶：基于关键点检测实现手姿态识别之--模型训练简易版本

上面的方法需要你会自己使用 pytorch 修改训练模型，以及量化转模型格式比较麻烦。
这里提供另外一种简单很多的曲线救国的方式，无需自己搭建环境训练和模型转换：
* 同上一个方法获取手相对于手左上角顶点的坐标。
* 基于这些点生成一幅图，不同的点可以用不同的颜色，具体请自行思考和尝试生成什么样的图比较好。
* 将生成的图片上传到[MaixHub.com](https://maixhub.com) 创建分类模型项目，在线训练，选择 MaixCAM 平台。
* 一键训练，完成后得到模型，后台会自动训练并转换成 MaixCAM 支持的格式。
* 修改例程，识别到关键点后，按照同样的方法生成图片，然后传给你训练的分类模型进行识别得到结果。


## 进阶：基于关键点检测实现手动作识别之--复杂动作

上面的是简单的动作，是单张图片识别，如果想时间轴维度上识别，比如识别画圆圈动作：
* 一种方法是把历史关键点存在队列中，根据队列中的关键点数据用代码来判断动作。
* 另外一种是将历史关键点作为一个序列输入到分类模型中，这样分类模型就可以识别时间轴上的动作了。
* 还可以将历史关键点合成一张图片给分类模型也可以。
