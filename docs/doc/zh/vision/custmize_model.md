---
title: MaixPy 自定义 AI 模型和运行
---


## 介绍

除了官方提供的或者社区开发者提供的模型以外，你也可以设计或者移植没有被支持的模型，然后使用 MaixPy 运行。

## 模型转换成设备支持的格式

当你有可以在电脑跑的模型，比如 onnx 模型，嵌入式设备算力有限一般来说不能直接运行，需要转换成设备支持的格式才能跑。

不同的设备转换方法不同，具体的请看对应设备平台的[模型转换方法文档](https://wiki.sipeed.com/ai/zh/deploy/index.html)。

## 模型统一描述文件 MUD

在前面可以看到模型文件都是 mud 格式的，这是一个描述文件，因为不同平台的模型格式大不相同，为了保证 MaixPy 的 API 保持统一，以及减小开发者的使用难度，规定了这样一个描述格式，比如 yolov5 在 MaixCAM 硬件平台上的模型格式为 cvimodel，以及还有一个标签文件，我们将这两个文件的路径和文件名写到 mud 文件中，用户调用酒只需要调用 mud 文件了，代码里不会出现 cvimodel 这种不跨平台的名称。

具体的 MUD 文件格式请看[NN 准则](https://github.com/Neutree/MaixCDK/blob/master/docs/doc/convention/nn.md)。


## MaixPy 中运行模型

前面的例程都是针对具体的模型，对于一般的通用模型， MaixPy 提供了 `load forward`等基础运行模型的函数。

```python
from maix import nn, image

model = nn.NN(model="/root/models/mobilenetv2.mud")
img = image.load("/root/dog.jpg")
outs = model.forward_image(img)
for out in outs:
    print(out)
```

更多请看 nn 模块的 API 文档。







