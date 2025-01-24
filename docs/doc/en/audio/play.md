---
title: MaixCAM MaixPy Playback Audio
update:
  - date: 2024-05-20
    author: lxowalle
    version: 1.0.0
    content: Initial document
---

## Introduction

This document provides instructions on how to play audio


## How to use

### Hardware operation

![image-20240520134637905](../../../static/image/maixcam_hardware_back.png)

The `MaixCAM` does not have a built-in speaker, so you will need to solder a `1W` speaker yourself. The pins for soldering the speaker are shown in the diagram above on the `VOP` and `VON` pins corresponding to the Speaker.

Note: If the `MaixCAM` has copper posts attached to these pins, they can be soldered directly to the posts, or on the other side of the board for aesthetic reasons.

### Code

#### Playing a `WAV` file

```python
from maix import audio, time, app

p = audio.Player("/root/output.wav")

p.play()
p.volume(80)
while not app.need_exit():
    time.sleep_ms(10)
print("play finish!")
```

Steps：


1. Import the audio, time and app modules:

   ```python
   from maix import audio, time, app
   ```

2. Initialize the player:

   ```python
   p = audio.Player("/root/output.wav")
   ```
  - Note that the default sample rate is 48k, the sample format is little-endian format - signed 16-bit, and the sample channel is 1. You can also customise the parameters like this `p = audio.Player(sample_rate=48000, format=audio.Format.FMT_S16_LE, channel = 1)`. So far only tested with sample rate 48000, format `FMT_S16_LE`, and number of sampling channels 1.
  - If it is a `.wav` file, the sample rate, sample format and sample channel are automatically obtained.
  - `p.volume(80)` set volume value to 80, range is [0~100].

3. Playing audio

   ```python
   p.play()
   ```

  - This operation will block until all audio data is written, but not until all audio data is actually played. If you exit the programme after calling `play()`, some of the audio data to be played may be lost.

4. Done


#### Playback with `PCM` data

```python
from maix import audio, time, app

p = audio.Player()

with open('/root/output.pcm', 'rb') as f:
    ctx = f.read()

p.play(bytes(ctx))

while not app.need_exit():
    time.sleep_ms(10)

print("play finish!")
```

Steps：


1. Import the audio, time and app modules:

   ```python
   from maix import audio, time, app
   ```

2. Initialize the player:

   ```python
   p = audio.Player()
   ```
  - Note that the default sample rate is 48k, the sample format is little-endian format - signed 16-bit, and the sample channel is 1. You can also customise the parameters like this `p = audio.Player(sample_rate=48000, format=audio.Format.FMT_S16_LE, channel = 1)`. So far only tested with sample rate 48000, format `FMT_S16_LE`, and number of sampling channels 1.

3. Open and playback a PCM file

   ```python
     with open('/root/output.pcm', 'rb') as f:
         ctx = f.read()
   
     p.play(bytes(ctx))
   
     while not app.need_exit():
       time.sleep_ms(10)
   ```

  - `with open(‘xxx’,‘rb’) as f:` open file `xxx` and get file object `f`
  - `ctx = f.read()` reads the contents of the file into `ctx`
  - `p.play(bytes(ctx))` plays the audio, `p` is the opened player object, `ctx` is the `PCM` data converted to type bytes
  - `time.sleep_ms(10)` Here there is a loop to wait for the playback to complete, as the playback operation is performed asynchronously, and if the program exits early, then it may result in the audio not being played completely.

4. Done