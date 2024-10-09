---
title: MaixCAM MaixPy Continuous Chinese digit recognition
update:
  - date: 2024-10-08
    author: 916BGAI
    version: 1.0.0
    content: Initial document
---

## Introduction

`MaixCAM` has ported the `Maix-Speech` offline speech library, enabling continuous Chinese numeral recognition, keyword recognition, and large vocabulary speech recognition capabilities. It supports audio recognition in `PCM` and `WAV` formats, and can accept input recognition via the onboard microphone.

## Maix-Speech

[`Maix-Speech`](https://github.com/sipeed/Maix-Speech) is an offline speech library specifically designed for embedded environments. It features deep optimization of speech recognition algorithms, achieving a significant lead in memory usage while maintaining excellent WER. For more details on the principles, please refer to the open-source project.

## Continuous Chinese digit recognition

```python
from maix import app, nn

speech = nn.Speech("/root/models/am_3332_192_int8.mud")
speech.init(nn.SpeechDevice.DEVICE_MIC, "hw:0,0")

def callback(data: str, len: int):
    print(data)

speech.digit(640, callback)

while not app.need_exit():
    frames = speech.run(1)
    if frames < 1:
        print("run out\n")
        speech.deinit()
        break
```

### Usage

1. Import the `app` and `nn` modules

```python
from maix import app, nn
```

2. Load the acoustic model

```python
speech = nn.Speech("/root/models/am_3332_192_int8.mud")
```

- You can also load the `am_7332` acoustic model; larger models provide higher accuracy but consume more resources.

3. Choose the corresponding audio device

```python
speech.init(nn.SpeechDevice.DEVICE_MIC, "hw:0,0")
```

- This uses the onboard microphone and supports both `WAV` and `PCM` audio as input devices.

```python
speech.init(nn.SpeechDevice.DEVICE_WAV, "path/audio.wav")   # Using WAV audio input
```

```python
speech.init(nn.SpeechDevice.DEVICE_PCM, "path/audio.pcm")   # Using PCM audio input
```

- Note that `WAV` must be `16KHz` sample rate with `S16_LE` storage format. You can use the `arecord` tool for conversion.

```shell
arecord -d 5 -r 16000 -c 1 -f S16_LE audio.wav
```

- When recognizing `PCM/WAV` , if you want to reset the data source, such as for the next WAV file recognition, you can use the `speech.devive` method, which will automatically clear the cache:


```python
speech.devive(nn.SpeechDevice.DEVICE_WAV, "path/next.wav")
```

4. Set up the decoder

```python
def callback(data: str, len: int):
    print(data)

speech.digit(640, callback)
```
- Users can register several decoders (or none), which decode the results from the acoustic model and execute the corresponding user callback. Here, a `digit` decoder is registered to output the Chinese digit recognition results from the last 4 seconds. The returned recognition results are in string format and support `0123456789 .(dot) S(ten) B(hundred) Q(thousand) W(thousand)`. For other decoder usages, please refer to the sections on Real-time voice recognition and keyword recognition.

- When setting the `digit` decoder, you need to specify a `blank` value; exceeding this value (in ms) will insert a `_` in the output results to indicate idle silence.

- After registering the decoder, use the `speech.deinit()` method to clear the initialization.

5. Recognition

```python
while not app.need_exit():
    frames = speech.run(1)
    if frames < 1:
        print("run out\n")
        speech.deinit()
        break
```

- Use the `speech.run` method to run speech recognition. The parameter specifies the number of frames to run each time, returning the actual number of frames processed. Users can choose to run 1 frame each time and then perform other processing, or run continuously in a single thread, stopping it with an external thread.

### Recognition Results

If the above program runs successfully, speaking into the onboard microphone will yield continuous Chinese digit recognition results, such as:

```shell
_0123456789
```