---
title: Whisper 语音识别模型
update:
  - date: 2026-01-05
    author: lxowalle
    version: 1.0.0
    content: 新增 Whisper 文档
---

## Whisper 模型简介

Whisper 是 OpenAI 开源的通用语音识别模型，可以把语音转换成文字。MaixCAM2 目前支持 `base` 版本，可识别中文和英文。

## 下载模型

| 模型 | 平台 | 内存需求 | 说明 |
| --- | --- | --- | --- |
| [whisper-base-maixcam2](https://huggingface.co/sipeed/whisper-base-maixcam2) | MaixCAM2 | 1 GB | base |

按照[大模型使用说明](./basic.md)下载并解压模型。

## MaixPy 运行模型

先准备一个单声道、16 kHz 采样率的 WAV 文件。单声道表示只有一个音频通道；16 kHz 表示每秒采样 16000 次。

确认模型和音频路径与设备上的实际位置一致，然后运行：

```python
from maix import nn

whisper = nn.Whisper(
    model="/root/models/whisper-base/whisper-base.mud",
    language="zh",
)

wav_path = "/maixapp/share/audio/demo.wav"
text = whisper.transcribe(wav_path)
print("result:", text)
```

`language="zh"` 表示识别中文。识别英文时改成 `language="en"`。如果提示找不到文件，请检查 `.mud` 模型路径和 WAV 音频路径。
