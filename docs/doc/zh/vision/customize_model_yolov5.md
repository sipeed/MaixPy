---
title: 为 MaixCAM MaixPy 离线训练 YOLOv5 模型，自定义检测物体
update:
    - date: 2024-6-20
      version: v1.0
      author: neucrack
      content:
        编写文档
    - date: 2025-7-01
      version: v2.0
      author: neucrack
      content:
        增加 MaixCAM2 支持
---


## 简介

默认官方提供了 80 种物体检测，如果不满足你的需求，可以自己训练检测的物体，两种方式：
* 使用 [MaixHub 在线训练](./maixhub_train.md)，方便快捷，无需购买服务器也无需搭建环境，点几下鼠标就完成。
* 在自己的电脑或者服务器搭建训练环境训练。

前者好处是简单快速，后者是使用自己电脑，训练图片数量不受限制，但是后者难度会大非常多。

**注意：** 本文讲了如何自定义训练，但是有一些基础知识默认你已经拥有，如果没有请自行学习：
* 本文不会讲解如何安装训练环境，请自行搜索安装（Pytorch 环境安装）测试。
* 本文不会讲解机器学习的基本概念、linux相关基础使用知识。

如果你觉得本文哪里需要改进，欢迎点击右上角`编辑本文`贡献并提交 文档 PR。


## 流程和本文目标

要想我们的模型能在 MaixPy (MaixCAM)上使用，需要经历以下过程：
* 搭建训练环境，本文略过，请自行搜索 pytorch 训练环境搭建。
* 拉取 [yolov5](https://github.com/ultralytics/yolov5) 源码到本地。
* 准备数据集，并做成 yolov5 项目需要的格式。
* 训练模型，得到一个 `onnx` 模型文件，也是本文的最终输出文件。
* 将`onnx`模型转换成 MaixPy 支持的 `MUD` 文件，这个过程在模型转换文章中有详细介绍：
  * [MaixCAM 模型转换](../ai_model_converter/maixcam.md)
  * [MaixCAM2 模型转换](../ai_model_converter/maixcam2.md)
* 使用 MaixPy 加载模型运行。



## 参考文章

因为是比较通用的操作过程，本文只给一个流程介绍，具体细节可以自行看 **[YOLOv5 官方代码和文档](https://github.com/ultralytics/yolov5)**(**推荐**)，以及搜索其训练教程，最终导出 onnx 文件即可。

这里有 MaixHub 的社区的几篇文章：
* [maixcam部署yolov5s 自定义模型](https://maixhub.com/share/23)
* [【流程分享】YOLOv5训练自定义数据集并部署在Maixcam上](https://maixhub.com/share/32)
* [yolov5猫狗识别模型——免费云训练（新手也可复现）](https://maixhub.com/share/25)

如果你有觉得讲得不错的文章欢迎修改本文并提交 PR。

## YOLOv5 导出 ONNX 模型文件

YOLOv5 提供了导出选项，直接在`yolov5`目录下执行
```shell
python export.py --weights ../yolov5s.pt --include onnx --img 224 320
```
这里加载 pt 参数文件，转换成 onnx， 同时指定分辨率，注意这里 高在前，宽在后。
模型训练的时候用的`640x640`，我们重新指定了分辨率方便提升运行速度，这里使用`320x224`的原因是和 MaixCAM 的屏幕比例比较相近方便显示，对于 MaixCAM2 可以用 `640x480` 或者 `320x240`，具体可以根据你的需求设置就好了。



## MaixCAM MUD 文件

将 onnx 转换为 `mud` 格式的模型文件时，参照 [MaixCAM 模型转换](../ai_model_converter/maixcam.md) 和 [MaixCAM2 模型转换](../ai_model_converter/maixcam2.md)  即可，最终会得到一个`mud`文件和`cvimodel`文件，其中 `mud` 文件内容：

MaixCAM/MaixCAM-Pro:
```ini
[basic]
type = cvimodel
model = yolov5s_320x224_int8.cvimodel

[extra]
model_type = yolov5
input_type = rgb
mean = 0, 0, 0
scale = 0.00392156862745098, 0.00392156862745098, 0.00392156862745098
anchors = 10,13, 16,30, 33,23, 30,61, 62,45, 59,119, 116,90, 156,198, 373,326
labels = person, bicycle, car, motorcycle, airplane, bus, train, truck, boat, traffic light, fire hydrant, stop sign, parking meter, bench, bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe, backpack, umbrella, handbag, tie, suitcase, frisbee, skis, snowboard, sports ball, kite, baseball bat, baseball glove, skateboard, surfboard, tennis racket, bottle, wine glass, cup, fork, knife, spoon, bowl, banana, apple, sandwich, orange, broccoli, carrot, hot dog, pizza, donut, cake, chair, couch, potted plant, bed, dining table, toilet, tv, laptop, mouse, remote, keyboard, cell phone, microwave, oven, toaster, sink, refrigerator, book, clock, vase, scissors, teddy bear, hair drier, toothbrush
```

MaixCAM2:
```ini
[basic]
type = axmodel
model_npu = yolov5s_640x480_npu.axmodel
model_vnpu = yolov5s_640x480_vnpu.axmodel

[extra]
model_type = yolov5
type=detector
input_type = rgb

input_cache = true
output_cache = true
input_cache_flush = false
output_cache_inval = true

anchors = 10,13, 16,30, 33,23, 30,61, 62,45, 59,119, 116,90, 156,198, 373,326
labels = person, bicycle, car, motorcycle, airplane, bus, train, truck, boat, traffic light, fire hydrant, stop sign, parking meter, bench, bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe, backpack, umbrella, handbag, tie, suitcase, frisbee, skis, snowboard, sports ball, kite, baseball bat, baseball glove, skateboard, surfboard, tennis racket, bottle, wine glass, cup, fork, knife, spoon, bowl, banana, apple, sandwich, orange, broccoli, carrot, hot dog, pizza, donut, cake, chair, couch, potted plant, bed, dining table, toilet, tv, laptop, mouse, remote, keyboard, cell phone, microwave, oven, toaster, sink, refrigerator, book, clock, vase, scissors, teddy bear, hair drier, toothbrush

mean = 0,0,0
scale = 0.00392156862745098, 0.00392156862745098, 0.00392156862745098
```

根据你训练的内容替换参数即可，比如你训练检测`0~9`数字，那么只需要替换`labels=0,1,2,3,4,5,6,7,8,9` 即可， 然后运行模型时将两个文件放在同一个目录下加载`mud`文件即可。


## 上传分享到 MaixHub

到 [MaixHub 模型库](https://maixhub.com/model/zoo?platform=maixcam) 上传并分享你的模型，可以多提供几个分辨率供大家选择。




