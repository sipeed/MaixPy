---
title: MaixCAM MaixPy 录音
update:
  - date: 2024-05-20
    author: lxowalle
    version: 1.0.0
    content: 
      - 初版文档
  - date: 2025-01-24
    author: lxowalle
    version: 1.0.1
    content: 
      - 更新audio模块的使用方法
---

## 简介

本文档提供录音的使用方法，支持录入`PCM`和`WAV`格式的音频。

- `PCM(Pulse Code Modulation)` 是一种数字音频编码格式，用于将模拟音频信号转换为数字信号，也是一般需要硬件处理所需的常用格式
- `WAV(Waveform Audio File Format)`是一种常见的音频文件格式。它通常用于存储未压缩的` PCM `音频数据，但也支持其他编码格式。

`MaixCAM`板载了麦克风，所以你可以直接使用录音功能。

### 硬件支持情况

| 设备        | 麦克风 | 喇叭 |
| ----------- | ------ | ---- |
| MaixCAM     | ✅      | ❌    |
| MaixCAM2    | ✅      | ✅    |
| MaixCAM Pro | ✅      | ✅    |

### 使用方法

#### 录制一个`PCM`/`WAV`格式的音频文件

在创建`Recorder`对象时传入了`path`， 则录入的音频将会保存到`path`文件中，你也可以通过`record`方法获取当前录入的`PCM`数据。`path`只支持`.pcm`和`.wav`后缀的路径。当录入`.wav`时，`record`方法不会返回`WAV`头部信息，只会返回`PCM`数据。

```python
from maix import audio

r = audio.Recorder("/root/test.wav")
r.volume(100)
print(f"channel: {r.channel()}")
print(f"sample rate: {r.sample_rate()}")

r.record(3000)
```

步骤：

1. 导入audio模块

   ```python
   from maix import audio
   ```

2. 初始化录制器

   ```python
   r = audio.Recorder("/root/test.wav")
   r.volume(100)
   ```

     - 音频文件会保存到`/root/test.wav`

     - 注意默认的采样率是48k，采样格式为小端格式-有符号16位，采样通道为1。你也可以像这样自定义参数`p = audio.Recorder(sample_rate=48000, format=audio.Format.FMT_S16_LE, channel = 1)`。目前只测试过采样率16000和48000，`FMT_S16_LE`格式，和采样通道数为1

     - `r.volume(100)`用来设置音量，音量范围为[0,100]

3. 开始录制

   ```python
   r.record(3000)
   ```

   - 录制`3000`毫秒的音频
   - 该函数会阻塞直到录入完成

4. 完成

#### 录制一个`PCM`/`WAV`格式的音频文件（非阻塞）

开发应用是如果需要录音，但又不希望录音函数占用其他应用的时间，则可以开启非阻塞模式

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

注意：

1. 非阻塞录制时，需要使用`reset(True)`函数来启用音频流，使用`reset(False)`函数来停止音频流

2. `record`返回的音频数据长度不一定与传入的时间对等，比如假设录制`50ms`音频，但此时音频缓冲区只有`20ms`的数据已经准备好了，那么`record(50)`只会返回`20ms`的音频数据

3. 如果希望record()返回的音频数据与传入参数相等，则可以让等待缓存区准备了足够的音频数据后再读取

   ```python
   remaining_frames = r.get_remaining_frames()
   need_frames = 50 * r.sample_rate() / 1000
   if remaining_frames > need_frames:
       data = r.record(50)
   ```

   使用`get_remaining_frames()`函数获取接收缓冲区剩余的帧数，注意返回的是帧数，不是字节数。通过`sample_rate()`获取音频采样率，并计算实际要读取的帧数。

#### 获取实时`PCM`音频流

开发需要处理音频数据的应用时，不需要保存文件，只需要获取`PCM`裸流的场景。要实现这个功能，只需要在创建`Recorder`时不传入路径即可。当然你也可以开启非阻塞模式。

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

代码含义基本同上。
