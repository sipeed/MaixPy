---
title: MaixCAM MaixPy AI 视觉基本知识
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

在 MaixPy 中使用视觉 AI 很简单，默认提供了常用的 AI 模型，不需要自己训练模型就可以直接使用，在[MaixHub 模型库](https://maixhub.com/model/zoo) 中选择`maixcam` 就可以找到。

并且在底层已经封装好的 API，只需要简单的调用就可以实现。

如果你想训练自己的模型，也可以先从[MaixHub 在线训练](https://maixhub.com/model/training/project) 开始，在线平台只需要点点点就能训练出模型，不需要购买昂贵的机器，不需要搭建复杂的开发环境，也不需要写代码，非常适合入门，也适合懒得翻代码的老手。

一般训练得到了模型文件，直接传输到设备上，调用 MaixPy 的 API 就可以使用了，具体的调用方法看后文。




