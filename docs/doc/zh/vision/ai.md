---
title: AI 视觉基本知识
update:
  - date: 2024-04-03
    author: neucrack
    version: 1.0.0
    content: 初版文档
---


## 简介

如果没有 AI 基础，在学习 AI 前可以先看[什么是人工智能(AI)和机器学习](https://wiki.sipeed.com/ai/zh/basic/what_is_ai.html) 了解一下 AI 的基本概念。

然后我们使用的视觉 AI 一般都是基于`深度神经网络学习`这个方法，有兴趣可以看看[深度神经网络（DNN）基础知识](https://wiki.sipeed.com/ai/zh/basic/dnn_basic.html)


## MaixPy 中使用视觉 AI

MaixPy 已经封装了常见视觉模型的运行接口。第一次体验时，不需要训练模型：到 [MaixHub 模型库](https://maixhub.com/model/zoo)选择自己的板子，下载现成模型即可。

如果现成模型不能识别你的目标，可以使用 [MaixHub 在线训练](./maixhub_train.md)，或者在电脑上训练。完整路线见[模型获取、上板和运行](../ai_model_converter/ai_model_deploy.md)。

模型准备好后，需要把完整模型包传到设备，再由对应的 MaixPy API 加载。后面的分类、检测和识别文档会给出具体代码。


