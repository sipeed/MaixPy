---
title: MaixCAM MaixPy 语音实时识别
update:
  - date: 2024-10-08
    author: 916BGAI
    version: 1.0.0
    content: 初版文档
  - date: 2025-05-13
    author: lxowalle
    version: 1.0.1
    content: 新增whisper的使用说明
---

## 简介

`MaixCAM` 移植了 `Maix-Speech` 离线语音库，实现了连续中文数字识别、关键词识别以及大词汇量语音识别功能。支持 `PCM` 和 `WAV` 格式的音频识别，且可通过板载麦克风进行输入识别。

此外，我们把 OpenAI 的语音识别模型 Whisper 移植到`MaixCAM2`上，即使是在资源比较有限的设备上，也能运行强大的语音转文字功能。

语音识别模型支持列表:

|         | MaixCAM | MaixCAM Pro | MaixCAM2 |
| ------- | ------- | ----------- | -------- |
| Whisper | ❌       | ❌           | ✅        |
| Speech  | ✅       | ✅           | ❌        |

## 使用Whisper做语音转文字

> MaixCAM和MaixCAM Pro不支持使用whisper模型

目前支持`base`尺寸的whisper模型，支持输入单通道、16k采样率的wav音频文件，支持识别中文和英文。下面是使用Whisper识别语音的简单示例：

```python
from maix import nn

whisper = nn.Whisper(model="/root/models/whisper-base/whisper-base.mud")

wav_path = "/maixapp/share/audio/demo.wav"

res = whisper.transcribe(wav_path)

print('res:', res)
```

注：
1. 首先需要导入nn模块才能创建Whisper模型对象
```python
from maix import nn
```
2. 选择需要加载的模型，目前支持base尺寸的whisper模型
```python
whisper = nn.Whisper(model="/root/models/whisper-base/whisper-base.mud")
```
3. 准备一个单通道、16k采样率的wav音频文件，并进行推理，推理结果会直接返回
```python
wav_path = "/maixapp/share/audio/demo.wav"
res = whisper.forward(wav_path)
print('whisper:', res)
```
4. 输出结果
```shell
whisper: 开始愉快的探索吧
```
5. 动手试试吧～

默认为识别中文，如果需要识别英文，在初始化对象时填入language参数
```python
whisper = nn.Whisper(model="/root/models/whisper-base/whisper-base.mud", language="en")
```

## Maix-Speech

[`Maix-Speech`](https://github.com/sipeed/Maix-Speech) 是一款专为嵌入式环境设计的离线语音识别库，针对语音识别算法进行了深度优化，显著降低内存占用，同时在识别准确率方面表现优异。详细说明请参考 [Maix-Speech 使用文档](https://github.com/sipeed/Maix-Speech/blob/master/usage_zh.md)。

### 连续大词汇量语音识别

```python
from maix import app, nn

speech = nn.Speech("/root/models/am_3332_192_int8.mud")
speech.init(nn.SpeechDevice.DEVICE_MIC)

def callback(data: tuple[str, str], len: int):
    print(data)

lmS_path = "/root/models/lmS/"

speech.lvcsr(lmS_path + "lg_6m.sfst", lmS_path + "lg_6m.sym", \
             lmS_path + "phones.bin", lmS_path + "words_utf.bin", \
             callback)

while not app.need_exit():
    frames = speech.run(1)
    if frames < 1:
        print("run out\n")
        break
```

### 使用方法

1. 导入 `app` 和 `nn` 模块

```python
from maix import app, nn
```

2. 加载声学模型

```python
speech = nn.Speech("/root/models/am_3332_192_int8.mud")
```

- 也可以加载 `am_7332` 声学模型，模型越大精度越高但是消耗的资源也越大

3. 选择对应的音频设备

```python
speech.init(nn.SpeechDevice.DEVICE_MIC)
speech.init(nn.SpeechDevice.DEVICE_MIC, "hw:0,0")   # 指定音频输入设备
```

- 这里使用的是板载的麦克风，也选择 `WAV` 和 `PCM` 音频作为输入

```python
speech.init(nn.SpeechDevice.DEVICE_WAV, "path/audio.wav")   # 使用 WAV 音频输入
```

```python
speech.init(nn.SpeechDevice.DEVICE_PCM, "path/audio.pcm")   # 使用 PCM 音频输入
```

- 注意 `WAV` 需要是 `16KHz` 采样，`S16_LE` 存储格式，可以使用 `arecord` 工具转换

```shell
arecord -d 5 -r 16000 -c 1 -f S16_LE audio.wav
```

- 在 `PCM/WAV` 识别时，如果想要重新设置数据源，例如进行下一个WAV文件的识别可以使用 `speech.device` 方法，内部会自动进行缓存清除操作：

```python
speech.device(nn.SpeechDevice.DEVICE_WAV, "path/next.wav")
```

4. 设置解码器

```python
def callback(data: tuple[str, str], len: int):
    print(data)

lmS_path = "/root/models/lmS/"

speech.lvcsr(lmS_path + "lg_6m.sfst", lmS_path + "lg_6m.sym", \
             lmS_path + "phones.bin", lmS_path + "words_utf.bin", \
             callback)
```
- 用户可以同时设置多个解码器，`lvcsr` 解码器用于输出连续语音识别结果（小于1024个汉字结果）。

- 设置 `lvcsr` 解码器时需要设置 `sfst` 文件路径，`sym` 文件路径（输出符号表），`phones.bin` 的路径（拼音表），和 `words.bin` 的路径（词典表）。最后还要设置一个回调函数用于处理解码出的数据。

- 如果不再需要使用某个解码器，可以通过调用 `speech.dec_deinit` 方法进行解除初始化。

```python
speech.dec_deinit(nn.SpeechDecoder.DECODER_LVCSR)
```

5. 识别

```python
while not app.need_exit():
    frames = speech.run(1)
    if frames < 1:
        print("run out\n")
        break
```

- 使用 `speech.run` 方法运行语音识别，传入的参数为每次运行的帧数，返回实际运行的帧数。用户可以选择每次运行1帧后进行其他处理，或在一个线程中持续运行，使用外部线程进行停止。

- 若需清除已识别结果的缓存，可以使用 `speech.clear` 方法。

- 在识别过程中切换解码器，切换后的第一帧可能会出现识别错误。可以使用 `speech.skip_frames(1)` 跳过第一帧，确保后续结果准确。

### 识别结果

如果上述程序运行正常，对板载麦克风说话，会得到实时语言识别结果，如：

```shell
### SIL to clear decoder!
('今天天气 怎么样 ', 'jin1 tian1 tian1 qi4 zen3 me yang4 ')
```