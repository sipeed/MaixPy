---
title: MaixPy 录音
update:
  - date: 2024-05-20
    author: lxowalle
    version: 1.0.0
    content: 初版文档
---

## 简介

本文档提供录音的使用方法



### 使用方法

一个录音的示例

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

   - `data`是`PCM`格式的`bytes`类型数据，保存了当前录入的音频。`PCM`格式在初始化`Recorder`对象时设置，见步骤2.

4. 完成，做自己的应用时可以对`r.record()`返回的`PCM`数据做语音处理。
