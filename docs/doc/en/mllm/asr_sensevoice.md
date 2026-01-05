---
title: Running the SenseVoice Model on MaixPy MaixCAM
update:
  - date: 2026-01-05
    author: lxowalle
    version: 1.0.0
    content: Added SenseVoice documentation
---

## SenseVoice Model Overview

SenseVoice is a multilingual audio recognition model that supports Chinese, English, Cantonese, Japanese, and Korean. It provides features including speech recognition, automatic language detection, emotion recognition, automatic punctuation, and streaming recognition.

## Downloading the Model

Supported models:

| Model                                                         | Platform     | Memory Requirement | Description              |
| ------------------------------------------------------------ | -------- | -------- | ----------------- |
| [sensevoice-maixcam2](https://huggingface.co/sipeed/sensevoice-maixcam2) | MaixCAM2 | 1G       | |

Refer to the [Large Model User Guide](./basic.md) to download the model.

## Running the Model with MaixPy

> Note: MaixPy version `4.12.3` or later is required

### Non-Streaming Recognition

```python
from maix import sensevoice

model_path = "/root/models/sensevoice-maixcam2"
client = sensevoice.Sensevoice(model=model_path+"/model.mud", stream=False)
client.start()
if client.is_ready(block=True) is False:
    print("Failed to start service or model.")
    exit()

audio_file = "/maixapp/share/audio/demo.wav"
text = client.refer(path=audio_file)
print(text)

# You can comment out this line of code, which will save time on the next startup. 
# But it will cause the background service to continuously occupy CMM memory.
client.stop()
```

Output:

```shell
开始愉快的探索吧。
```

Explanation:
- When creating the `sensevoice.Sensevoice` object, setting `stream=False` enables non-streaming recognition. The interface will wait until recognition is complete and then return the result at once.
- When the `refer` function is called with the `path` parameter, it recognizes an audio file. Currently, only the `wav` format is supported. Audio format requirements: `16,000` Hz sample rate, mono channel, 16-bit width.
- When the `refer` function is called with the `audio_data` parameter, it recognizes `bytes-type PCM` data. Audio format requirements are the same: `16,000` Hz sample rate, mono channel, 16-bit width.
- The start function starts the `SenseVoice` background service, and the `stop` function stops it. Running `SenseVoice` as a background service allows multi-process operation and prevents the foreground application from being blocked during model execution.

### Streaming Recognition

```python
from maix import sensevoice

model_path = "/root/models/sensevoice-maixcam2"
client = sensevoice.Sensevoice(model=model_path+"/model.mud", stream=True)
client.start()
if client.is_ready(block=True) is False:
    print("Failed to start service or model.")
    exit()

audio_file = "/maixapp/share/audio/demo.wav"
print('start refer stream')
for text in client.refer_stream(path=audio_file):
    print(text)

# You can comment out this line of code, which will save time on the next startup. 
# But it will cause the background service to continuously occupy CMM memory.
client.stop()
```
Output:

```shell
开始愉快
开始愉快的探索
开始愉快的探索吧
```

Explanation:
- When creating the `sensevoice.Sensevoice` object, setting `stream=True` enables streaming recognition. Partial recognition results are returned immediately as they become available, until the entire audio is processed.
- Other behaviors are the same as described above.

### Real-Time Speech Recognition via Microphone

In practical development, you may need to capture audio data from a microphone and pass it to the model for speech-to-text processing. Please refer to the example:[asr_sensevoice.py](https://github.com/sipeed/MaixPy/tree/main/examples/audio/asr/sensevoice/asr_sensevoice.py)
