---
title: MaixCAM MaixPy 录音
update:
  - date: 2024-05-20
    author: lxowalle
    version: 1.0.0
    content: 初版文档
---

## 简介

本文档提供录音的使用方法，支持录入`PCM`和`WAV`格式的音频。

`MaixCAM`板载了麦克风，所以你可以直接使用录音功能。

### 使用方法

####  获取`PCM`数据

当构造`Recorder`对象时不传入`path`， 则只会录入音频后不会保存到文件中，当然你可以手动保存到文件。

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

步骤：

1. 导入audio、time和app模块

   ```python
   from maix import audio, time, app
   ```

2. 初始化录制器

   ```python
   r = audio.Recorder()
   r.volume(12)
   ```

     - 注意默认的采样率是48k，采样格式为小端格式-有符号16位，采样通道为1。你也可以像这样自定义参数`p = audio.Recorder(sample_rate=48000, format=audio.Format.FMT_S16_LE, channel = 1)`。目前只测试过采样率48000，`FMT_S16_LE`格式，和采样通道数为1

     - `r.volume(12)`用来设置音量，音量范围为[0,24]

3. 开始录制

   ```python
   data = r.record()
   ```

   - `data`是`PCM`格式的`bytes`类型数据，保存了当前录入的音频。`PCM`格式在初始化`Recorder`对象时设置，见步骤2。注意如果录制太快，音频缓冲区没有数据， 则有可能返回一个空的`bytes`数据。

4. 完成，做自己的应用时可以对`r.record()`返回的`PCM`数据做语音处理。



#### 录制音频并保存为`WAV`格式

当构造`Recorder`对象时传入了`path`， 则录入的音频将会保存到`path`文件中，并且你也可以通过`record`方法获取当前录入的`PCM`数据。`path`只支持`.pcm`和`.wav`后缀的路径，并且当录入`.wav`时，`record`方法不会返回`WAV`头部信息，只会返回`PCM`数据。

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

代码含义基本同上。



#### 录制音频并保存为`WAV`格式（阻塞）

录入时如果设置了`record_ms`参数，录入音频会阻塞直到到达`record_ms`设置的时间，单位ms。

```python
from maix import audio, time, app

r = audio.Recorder("/root/output.wav")
r.volume(12)
print("sample_rate:{} format:{} channel:{}".format(r.sample_rate(), r.format(), r.channel()))

r.record(5000)
print("record finish!")
```

上面示例将会持续录入`5000`ms，并保存为`WAV`格式，录入期间将会阻塞在`record`方法中，注意当`record`设置了`record_ms`后不会返回`PCM`数据。

### 其他

`Player`和`Recorder`模块有些`bug`待解决，请保证它们在其他模块（`Camera`模块，`Display`模块等）之前创建。例如：

```python
# 先创建Player和Recorder
p = audio.Player()
r = audio.Recorder()

# 再创建Camera
c = camera.Camera()
```
