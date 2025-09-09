---
title: MaixCAM MaixPy Audio Record
update:
  - date: 2024-05-20
    author: lxowalle
    version: 1.0.0
    content: Initial document
  - date: 2025-01-24
    author: lxowalle
    version: 1.0.1
    content:
      - Update the usage instructions for the audio module.
---

## Introduction

This document provides instructions on how to use the recording feature, supporting the recording of audio in both `PCM` and `WAV` formats.

`PCM (Pulse Code Modulation)` is a digital audio encoding format used to convert analog audio signals into digital signals. It is also the commonly required format for general hardware processing.

`WAV (Waveform Audio File Format)` is a popular audio file format. It is typically used to store uncompressed `PCM` audio data but also supports other encoding formats.

The MaixCAM board comes with a built-in microphone, so you can directly use the recording feature.

### Hardware Support

| Device      | Microphone | Speaker |
| ----------- | ---------- | ------- |
| MaixCAM     | ✅          | ❌       |
| MaixCAM2    | ✅          | ✅       |
| MaixCAM Pro | ✅          | ✅       |

### How to use

#### Record an Audio File in `PCM`/`WAV` Format

If you don't pass `path` when constructing a `Recorder` object, it will only record audio and not save it to a file, but you can save it to a file manually.

```python
from maix import audio

r = audio.Recorder("/root/test.wav")
r.volume(100)
print(f"channel: {r.channel()}")
print(f"sample rate: {r.sample_rate()}")

r.record(3000)
```

Steps：

1. Import the audio, time and app modules:

   ```python
   from maix import audio, time, app
   ```

2. Initialize Recorder

   ```python
   r = audio.Recorder("/root/test.wav")
   r.volume(100)
   ```

    - Note that the default sample rate is 48k, the sample format is little-endian format - signed 16-bit, and the sample channel is 1. You can also customise the parameters like this `r = audio.Recorder(sample_rate=48000, format=audio.Format.FMT_S16_LE, channel = 1)`. So far only tested with sample rate 16000 and 48000, format `FMT_S16_LE`, and number of sampling channels 1.

     - `r.volume(100)` is used to set the volume, the volume range is [0,100]

3. Start recording

   ```python
   r.record(3000)
   ```

   - Record audio for 3000 milliseconds.

   - This function will block until the recording is complete.

4. Done

#### Record an Audio File in `PCM`/`WAV` Format (Non-blocking)

When developing applications, if you need to record audio but do not want the recording function to occupy time for other applications, you can enable non-blocking mode.

```python
from maix import audio, app, time

r = audio.Recorder("/root/test.wav", block=False)
r.volume(100)
r.reset(True)

while not app.need_exit():
    data = r.record(50)
    // Your application
    time.sleep_ms(50)

print("finish!")
```

**Notes:**

1. In non-blocking recording, you need to use the `reset(True)` function to enable the audio stream and the `reset(False)` function to stop the audio stream.

2. The length of the audio data returned by `record` may not match the input time. For example, if you request to record `50ms` of audio but only `20ms` of data is ready in the audio buffer, then `record(50)` will only return `20ms` of audio data.

3. If you want the audio data returned by `record()` to match the input parameter, you can wait until the buffer has enough audio data before reading.

   ```python
   remaining_frames = r.get_remaining_frames()
   need_frames = 50 * r.sample_rate() / 1000
   if remaining_frames > need_frames:
       data = r.record(50)
   ```

   Use the `get_remaining_frames()` function to get the number of remaining frames in the receive buffer. Note that this returns the number of frames, not bytes. Use `sample_rate()` to get the audio sample rate and calculate the actual number of frames to read.

#### Obtain Real-time `PCM` Audio Stream

When developing applications that need to process audio data, you may not need to save files but only require the raw `PCM` stream. To achieve this, simply do not provide a path when creating the `Recorder`. Of course, you can also enable non-blocking mode.

```python
from maix import audio, app, time

r = audio.Recorder(block=False)
r.volume(100)
r.reset(True)

while not app.need_exit():
    data = r.record(50)
    print(f'record {len(data)} bytes')
    // Your application
    time.sleep_ms(50)
```

The code logic is essentially the same as above.