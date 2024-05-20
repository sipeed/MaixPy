---
title: MaixPy Audio Record
update:
  - date: 2024-05-20
    author: lxowalle
    version: 1.0.0
    content: Initial document
---

## Introduction

This document provides methods for recording

### How to use

An example of a recording

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

   - `data` is `bytes` type data in `PCM` format that holds the currently recorded audio. The `PCM` format is set when initialising the `Recorder` object, see step 2.

4. Done, you can do voice processing on the `PCM` data returned by `r.record()` when doing your own applications.
