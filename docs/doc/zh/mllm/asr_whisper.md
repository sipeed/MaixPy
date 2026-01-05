---
title: MaixPy MaixCAM 运行 Whisper 模型
update:
  - date: 2026-01-05
    author: lxowalle
    version: 1.0.0
    content: 新增 Whisper 文档
---

## Whisper 模型简介

Whisper是OpenAI公司开源的一个通用语音识别模型，用于多语言识别、语音翻译等任务。目前MaixCAM2移植的 Whisper 模型为`base`版本，支持输入单通道、16k采样率的wav音频文件，支持识别中文和英文。

## 下载模型

支持列表：

| 模型                                                         | 平台     | 内存需求 | 说明              |
| ------------------------------------------------------------ | -------- | -------- | ----------------- |
| [whisper-base-maixcam2](https://huggingface.co/sipeed/whisper-base-maixcam2) | MaixCAM2 | 1G      | base |

参考[大模型使用说明](./basic.md)下载模型

## MaixPy 运行模型

目前支持`base`尺寸的whisper模型，支持输入单通道、16k采样率的wav音频文件，支持识别中文和英文。下面是使用Whisper识别语音的简单示例：

```python
from maix import nn

whisper = nn.Whisper(model="/root/models/whisper-base-maixcam2/whisper-base.mud")

wav_path = "/maixapp/share/audio/demo.wav"

res = whisper.transcribe(wav_path)

print('res:', res)
```

注：
1. 首先需要导入nn模块才能创建Whisper模型对象
```python
from maix import nn
```
2. 选择需要加载的模型，目前支持base尺寸的whisper模型
```python
whisper = nn.Whisper(model="/root/models/whisper-base/whisper-base-maixcam2.mud")
```
3. 准备一个单通道、16k采样率的wav音频文件，并进行推理，推理结果会直接返回
```python
wav_path = "/maixapp/share/audio/demo.wav"
res = whisper.forward(wav_path)
print('whisper:', res)
```
4. 输出结果
```shell
whisper: 开始愉快的探索吧
```

默认为识别中文，如果需要识别英文，在初始化对象时填入language参数
```python
whisper = nn.Whisper(model="/root/models/whisper-base-maixcam2/whisper-base.mud", language="en")
