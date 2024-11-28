---
title: MaixCAM MaixPy 使用 AI 模型进行物体分类
---

## 物体分类概念

比如眼前有两张图片，一张图里面是苹果，另一张是飞机，物体分类的任务就是把两张图分别依次输入给 AI 模型，模型会依次输出两个结果，一个是苹果，一个是飞机。

## MaixPy 中使用物体分类

MaixPy 默认提供了 `imagenet` 数据集训练得到的 `1000`分类模型，可以直接使用：
```python
from maix import camera, display, image, nn

classifier = nn.Classifier(model="/root/models/mobilenetv2.mud", dual_buff = True)
cam = camera.Camera(classifier.input_width(), classifier.input_height(), classifier.input_format())
disp = display.Display()

while 1:
    img = cam.read()
    res = classifier.classify(img)
    max_idx, max_prob = res[0]
    msg = f"{max_prob:5.2f}: {classifier.labels[max_idx]}"
    img.draw_string(10, 10, msg, image.COLOR_RED)
    disp.show(img)
```

效果视频:

<video playsinline controls autoplay loop muted preload src="/static/video/classifier.mp4" type="video/mp4">
Classifier Result video
</video>

这里使用了摄像头拍摄图像，然后传给 `classifier`进行识别，得出结果后，将结果显示在屏幕上。

更多 API 使用参考 [maix.nn](/api/maix/nn.html) 模块的文档。


## dual_buff 双缓冲区加速

你可能注意到这里模型初始化使用了`dual_buff`（默认值就是 `True`），使能 `dual_buff` 参数可以加快运行效率，提高帧率，具体原理和使用注意点见 [dual_buff 介绍](./dual_buff.md)。

## 使用 MaixHub 训练自己的分类模型

如果你想训练特定图像的分类模型，请到[MaixHub](https://maixhub.com) 学习并训练分类模型，创建项目时选择`分类模型`，然后上传图片训练即可，无需搭建训练环境也无需花钱购买昂贵的GPU，快速一键训练。

## 离线训练自己的分类模型

离线训练需要自己搭建环境，请自行搜索 `PyTorch 分类模型训练` `Mobilenet`等相关关键字进行参考。
训练好模型后导出 onnx 格式的模型，然后参考 [MaixCAM 模型转换文档](../ai_model_converter/maixcam.md) 转换为 MaixCAM 支持的模型格式，最后使用上面的`nn.Classifier`类加载模型即可。

这里分类模型可以是 mobilenet 也可以是 其它模型比如 Resnet 等，模型转换时最好提取 `softmax`前一层作为最后的输出层，因为`classifier.classify(img, softmax=True)` 识别函数的`softmax`参数默认为`True`，即会对结果计算一次`softmax`，所以模型就不用`softmax`这一层了，当然如果模型包含了`softmax`层，也可以指定不再执行一遍`softmax`： `classifier.classify(img, softmax=False)`。

