---
title: Running the Whisper Model on MaixPy MaixCAM
update:
  - date: 2026-01-05
    author: lxowalle
    version: 1.0.0
    content: Added Whisper documentation
---

## Whisper Model Overview

Whisper is a general-purpose speech recognition model open-sourced by OpenAI, designed for tasks such as multilingual speech recognition and speech translation.
Currently, the Whisper model ported to MaixCAM2 is the `base` version. It supports input WAV audio files with mono channel and 16 kHz sample rate, and can recognize Chinese and English.

## Downloading the Model

Supported models:

| Model                                                         | Platform     | Memory Requirement | Description              |
| ------------------------------------------------------------ | -------- | -------- | ----------------- |
| [whisper-base-maixcam2](https://huggingface.co/sipeed/whisper-base-maixcam2) | MaixCAM2 | 1G      | base |

Refer to the [Large Model User Guide](./basic.md) to download the model.

## Running the Model with MaixPy

Currently, only the base-size Whisper model is supported. It accepts mono, 16 kHz WAV audio files and supports Chinese and English recognition.
Below is a simple example demonstrating how to use Whisper for speech recognition:

```python
from maix import nn

whisper = nn.Whisper(model="/root/models/whisper-base-maixcam2/whisper-base.mud")

wav_path = "/maixapp/share/audio/demo.wav"

res = whisper.transcribe(wav_path)

print('res:', res)
```

Notes:
1. First, import the nn module to create a Whisper model object:
```python
from maix import nn
```
2. Select the model to load. Currently, only the base-size Whisper model is supported:
```python
whisper = nn.Whisper(model="/root/models/whisper-base-maixcam2/whisper-base.mud")
```
3. Prepare a mono, 16 kHz WAV audio file and run inference. The recognition result will be returned directly:
```python
wav_path = "/maixapp/share/audio/demo.wav"
res = whisper.forward(wav_path)
print('whisper:', res)
```
4. Output result:
```shell
whisper: 开始愉快的探索吧
```

By default, the model recognizes Chinese.
To recognize English, specify the `language` parameter when initializing the object:
```python
whisper = nn.Whisper(model="/root/models/whisper-base/whisper-base-maixcam2.mud", language="en")
