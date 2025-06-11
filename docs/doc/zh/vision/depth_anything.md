---
title: MaixCAM2 MaixPy 使用 Depth-Anything 单目估计深度距离
update:
  - date: 2025-06-09
    version: v1.0
    author: neucrack
    content: 增加 Depth-Anything-V2 代码和文档支持
---


## 简介

[Depth-Anything-V2](https://github.com/DepthAnything/Depth-Anything-V2) 可以将普通图片估计得到深度图，而且相较于 Depth-Anything-V1 在细节方面有所提升，以及一些材质上的优化比如玻璃，具体介绍可以看[官方开源仓库](https://github.com/DepthAnything/Depth-Anything-V2)或者[Web主页](https://depth-anything-v2.github.io/)。

<video playsinline controls autoplay loop muted preload src="../../assets/depth_anything_v2.mp4" type="video/mp4" style="min-height:0">
depth_anything_v2.mp4
</video>

## 支持的设备

| 设备      | 是否支持 |
| -------- | ------- |
| MaixCAM2 | ✅ |
| MaixCAM  | ❌ |



## 在 MaixCAM2 MaixPy 上使用 Depth-Anything

MaixPy 支持 Depth-Anything-V2，注意 MaixCAM 一代硬件不支持。

默认系统已经内置了模型，直接运行代码即可：
```python
from maix import camera, display, image, nn, app

cmap = image.CMap.TURBO
model = nn.DepthAnything(model="/root/models/depth_anything_v2_vits.mud", dual_buff = True)

cam = camera.Camera(model.input_width(), model.input_height(), model.input_format())
disp = display.Display()

while not app.need_exit():
    img = cam.read()
    res = model.get_depth_image(img, image.Fit.FIT_CONTAIN, cmap)
    if res:
        disp.show(res)
```

这里通过`get_depth_image` 直接获得一张伪彩色图像，`cmap`可以指定为彩色，支持的所有伪彩色可以看`maix.image.CMap` API 文档。

当然，如果你想要模型原始输出，也可以用`get_depth`方法获取 `float32` 类型的原始数据，可以将返回的数据通过`maix.tensor.tensor_to_numpy_float32`转换为`numpy`格式使用。

MaixCAM2 实机运行效果：
![](../../assets/depth_anything_v2_maixcam2.jpg)

## 注意点

注意 Depth-Anything-V2 是针对图片进行深度估计，输出原始数据是一个相对值，值范围会根据图像内容变化，比如 深度差距不大时为 0.0~2.0, 图像内容深度变化大时为 0.0~8.0，最后转为图片标准化值到 0～255。
所以对于视频和连续的图像帧来说，深度绝对值会变动，也就是你会看到的当用摄像头图像进行连续深度估计时输出图像会有轻微的闪动。


## 更多输入分辨率

由于模型需要的算力比较大，默认采用的分辨率为 448x336, 如果你期望使用其它分辨率，可以到[MaixHub 模型库](https://maixhub.com/model/zoo?platform=maixcam2)下载现有的其它分辨率的，如果 MaixHub 也没有你要的分辨率，可以自己转换模型。
对于 MaixCAM2，转换模型 参考[模型量化文档](../ai_model_converter/maixcam2.md) 以及 [huggingface.co/AXERA-TECH/Depth-Anything-V2](https://huggingface.co/AXERA-TECH/Depth-Anything-V2/tree/main) 和 [github.com/AXERA-TECH/DepthAnythingV2.axera](https://github.com/AXERA-TECH/DepthAnythingV2.axera)（注意 这个工程里 config.json 中输入是 BGR，建议改成MaixPy 默认使用的 RGB）。

