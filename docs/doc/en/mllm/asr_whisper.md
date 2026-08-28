---
title: Whisper Speech-Recognition Model
update:
  - date: 2026-01-05
    author: lxowalle
    version: 1.0.0
    content: Added Whisper documentation
---

## Whisper Model Overview

Whisper is an open-source speech-recognition model from OpenAI that converts speech into text. MaixCAM2 currently supports the `base` version for Chinese and English.

## Download the Model

| Model | Platform | Memory Required | Description |
| --- | --- | --- | --- |
| [whisper-base-maixcam2](https://huggingface.co/sipeed/whisper-base-maixcam2) | MaixCAM2 | 1 GB | base |

Follow the [Large Model User Guide](./basic.md) to download and extract the model.

## Run the Model with MaixPy

Prepare a mono WAV file sampled at 16 kHz. Mono means one audio channel; 16 kHz means 16,000 samples per second.

Make sure the model and audio paths match their actual locations on the device, then run:

```python
from maix import nn

whisper = nn.Whisper(
    model="/root/models/whisper-base/whisper-base.mud",
    language="en",
)

wav_path = "/maixapp/share/audio/demo.wav"
text = whisper.transcribe(wav_path)
print("result:", text)
```

Use `language="zh"` for Chinese or `language="en"` for English. If a file-not-found error appears, check both the `.mud` model path and WAV audio path.
