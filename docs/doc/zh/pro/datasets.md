---
title: MaixCAM MaixPy 训练模型哪里能找到模型和数据集
---

## 哪里找 MaixPy MaixCAM 直接能使用的模型

到[MaixHub 模型库](https://maixhub.com/model/zoo) 筛选对应的硬件平台即可找到。

## 数据集有什么用

可以先到[MaixHub 模型库](https://maixhub.com/model/zoo)看看有没有你需要的模型，如果没有，你可以自己训练模型，训练模型需要数据集，数据集就是用来训练模型的。

## 转换已有的模型给 MaixCAM MaixPy 使用

MaixPy 默认支持了一些模型框架，比如 YOLOv8/YOLO11/Mobilenet 等等，所以只要是这些框架训练的模型，只需要导出成 ONNX 格式再转换为 MaixCAM 支持的格式后 MaixPy MaixCAM 就可以使用了。

一些常见的数据，不自己训练，网上可以找到开源分享的训练好的预训练模型，比如 YOLO11/YOLOv8/YOLOv5 就会有很多，比如[这里](https://github.com/Eric-Canas/qrdet/releases)可以下载到检测二维码的 YOLOv8 与训练模型(qrdet-*.pt)，直接拿来导出成 ONNX 格式再转换为 [MaixCAM 支持的格式](https://maixhub.com/model/zoo/480)即可。

转换方法看[MaixCAM 模型转换文档](../ai_model_converter/maixcam.md)。

## 哪里找数据集

* 方法一：去算法官方官方找数据集。
比如对于 YOLO11/YOLOv8， [YOLO 官方文档-数据集](https://docs.ultralytics.com/datasets/) 中可以看到有很多开源数据集，按照其文档使用一行命令就能快速训练。同样导出 ONNX 格式再转换为 MaixCAM 支持的格式即可。
* 方法二：去数据集网站获取。
比如 [Kaggle](https://www.kaggle.com/datasets/riondsilva21/hand-keypoint-dataset-26k)、 [roboflow](https://universe.roboflow.com/)等等。
* 方法三：找开源数据集制作成模型训练脚本（比如 YOLO）支持的格式。




