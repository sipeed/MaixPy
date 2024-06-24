---
title: MaixPy Audio Record
update:
  - date: 2024-05-20
    author: lxowalle
    version: 1.0.0
    content: Initial document
---

## Introduction

This document provides the usage of audio recording and supports recording audio in `PCM` and `WAV` formats.

The `MaixCAM` has a microphone on board, so you can use the recording function directly.

### How to use

#### Getting `PCM` data

If you don't pass `path` when constructing a `Recorder` object, it will only record audio and not save it to a file, but you can save it to a file manually.

```python
from maix import audio, time, app

r = audio.Recorder()
r.volume(12)
print("sample_rate:{} format:{} channel:{}".format(r.sample_rate(), r.format(), r.channel()))

while not app.need_exit():
    data = r.record()
    print("data size", len(data))

    time.sleep_ms(10)

print("record finish!")
```

Steps：

1. Import the audio, time and app modules:

   ```python
   from maix import audio, time, app
   ```

2. Initialize Recorder

   ```python
   r = audio.Recorder()
   r.volume(12)
   ```

    - Note that the default sample rate is 48k, the sample format is little-endian format - signed 16-bit, and the sample channel is 1. You can also customise the parameters like this `r = audio.Recorder(sample_rate=48000, format=audio.Format.FMT_S16_LE, channel = 1)`. So far only tested with sample rate 48000, format `FMT_S16_LE`, and number of sampling channels 1.

     - `r.volume(12)` is used to set the volume, the volume range is [0,24]

3. Start recording

   ```python
   data = r.record()
   ```

   - `data` is `bytes` type data in `PCM` format that holds the currently recorded audio. The `PCM` format is set when initialising the `Recorder` object, see step 2. Note that if the recording is too fast and there is no data in the audio buffer, it is possible to return an empty `bytes` of data.

4. Done, you can do voice processing on the `PCM` data returned by `r.record()` when doing your own applications.

#### Records audio and saves it in `WAV` format.

If you pass `path` when constructing a `Recorder` object, the recorded audio will be saved to a `path` file, and you can also get the currently recorded `PCM` data via the `record` method. `path` only supports paths with `.pcm` and `.wav` suffixes, and the `record` method does not return `WAV` headers when recording `.wav`, it only returns `PCM` data.

```python
from maix import audio, time, app

r = audio.Recorder("/root/output.wav")
r.volume(12)
print("sample_rate:{} format:{} channel:{}".format(r.sample_rate(), r.format(), r.channel()))

while not app.need_exit():
    data = r.record()
    print("data size", len(data))

    time.sleep_ms(10)

print("record finish!")
```

The code means basically the same as above.

#### Record audio and save to `WAV` format (blocking)

If the `record_ms` parameter is set during recording, recording audio will block until the time set by `record_ms` is reached, unit: ms.

```python
from maix import audio, time, app

r = audio.Recorder("/root/output.wav")
r.volume(12)
print("sample_rate:{} format:{} channel:{}".format(r.sample_rate(), r.format(), r.channel()))

r.record(5000)

print("record finish!")
```

The above example will keep recording `5000`ms and save it to `WAV` format, during the recording period it will block in `record` method, note that `PCM` data will not be returned when `record` is set to `record_ms`.

### Other

The `Player` and `Recorder` modules have some `bugs` to be worked out, make sure they are created before other modules (`Camera` module, `Display` module, etc.). For example:

```python
# Create Player and Recorder first.
p = audio.Player()
r = audio.Recorder()

# Then create the Camera
c = camera.Camera()
```
