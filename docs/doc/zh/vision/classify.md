---
title: MaixPy 使用 AI 模型进行物体分类
---

## 物体分类概念

比如眼前有两张图片，一张图里面是苹果，另一张是飞机，物体分类的任务就是把两张图分别依次输入给 AI 模型，模型会依次输出两个结果，一个是苹果，一个是飞机。

## MaixPy 中使用物体分类

MaixPy 默认提供了 `imagenet` 数据集训练得到的 `1000`分类模型，可以直接使用：
```python
from maix import camera, display, image, nn

classifier = nn.Classifier(model="/root/models/mobilenetv2.mud")
cam = camera.Camera(classifier.input_width(), classifier.input_height(), classifier.input_format())
dis = display.Display()

while 1:
    img = cam.read()
    res = classifier.classify(img)
    max_idx, max_prob = res[0]
    msg = f"{max_prob:5.2f}: {classifier.labels[max_idx]}"
    img.draw_string(10, 10, msg, image.COLOR_RED)
    dis.show(img)
```

效果视频:

<video playsinline controls autoplay loop muted preload src="https://wiki.sipeed.com/maixpy/static/video/classifier.mp4" type="video/mp4">
Classifier Result video
</video>

这里使用了摄像头拍摄图像，然后传给 `classifier`进行识别，得出结果后，将结果显示在屏幕上。

更多 API 使用参考 [maix.nn](/api/maix/nn.html) 模块的文档。


## 训练自己的分类模型

请到[MaixHub](https://maixhub.com) 学习并训练分类模型，创建项目时选择`分类模型`即可。

