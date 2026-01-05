---
title: MaixPy MaixCAM 运行 SenseVoice 模型
update:
  - date: 2026-01-05
    author: lxowalle
    version: 1.0.0
    content: 新增 SenseVoice 文档
---

## SenseVoice 模型简介

SenseVoice是一个多语言音频识别模型，支持中文、英文、粤语、日语、韩语，包含的功能有语音识别、自动识别语言、情感识别、自动标点并且支持流式识别

## 下载模型

支持列表：

| 模型                                                         | 平台     | 内存需求 | 说明              |
| ------------------------------------------------------------ | -------- | -------- | ----------------- |
| [sensevoice-maixcam2](https://huggingface.co/sipeed/sensevoice-maixcam2) | MaixCAM2 | 1G       | |

参考[大模型使用说明](./basic.md)下载模型

## MaixPy 运行模型

> 注意:必须要`MaixPy 4.12.3`以上版本才支持

### 非流式识别

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

输出：

```shell
开始愉快的探索吧。
```

说明：

- 创建`sensevoice.Sensevoice`对象时传入`stream=False`表示开启非流式识别，此时接口将会等待识别完成后一次性返回结果
- `refer`函数传入`path`参数时将会识别一个音频文件， 目前只支持`wav`格式，音频格式要求：采样率为`16000`，单通道，16位宽
- `refer`函数传入`audio_data`参数时将会识别一个`bytes`类型的`pcm`数据， 音频格式要求：采样率为`16000`，单通道，16位宽
- `start`函数用于开启`sensevoice`的后台服务， `stop`函数用户关闭`sensevoice`的后台服务，将`sensevoice`识别过程做成后台服务的优点是能实现多进程操作， 在模型运行过程中不会阻塞前台进程的应用。

### 流式识别

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
输出:

```shell
开始愉快
开始愉快的探索
开始愉快的探索吧
```

说明：

- 创建`sensevoice.Sensevoice`对象时传入`stream=True`表示开启流式识别，此时接口将会识别到一部分结果后就会立即返回， 直到识别完所有音频
- 其他同上

### 通过麦克风实时识别语音

实际开发时可能需要捕获麦克风的音频数据，并交给模型做语音转文本，使用方法请查看示例：[asr_sensevoice.py](https://github.com/sipeed/MaixPy/tree/main/examples/audio/asr/sensevoice/asr_sensevoice.py)
