---
title: MaixCAM MaixPy 语音合成
update:
  - date: 2025-08-15
    author: lxowalle
    version: 1.0.0
    content: 初版文档
---

## 简介

本文档提供内置TTS的使用方法，以支持将文本转为语音的功能。

TTS支持列表

|       | MaixCAM | MaixCAM Pro | MaixCAM2 |
| ------- | ------- | ----------- | -------- |
| MeloTTS  | ❌ | ❌ | ✅ |

## TTS介绍

TTS(Text to speech)的作用是把文本转为语音,你可以编辑一段文本,然后交给支持TTS的模型,运行模型后会输出内容为该文本的音频数据.
现实常用TTS来实现视频配音,地图导航,公共场合播报等等.简单理解TTS就是“把文字念出来的技术”

## MelloTTS

MeloTTS是由MIT和MyShell.ai联合开发的一款高质量多语言文本转语音库. 目前支持`melotts-zh`模型, 该模型支持中英文语音合成, 但是英文合成的效果还不太好.

默认输出音频为采样率44100, 单通道, 16位采样深度的PCM数据.

> 采样率: 每秒采集声音的次数
>
> 通道: 每次采集声音的声道数. 单通道可以认为是采集单声道的音频, 双通道可以是采集左右两个声道的音频. 为了降低AI推理的复杂度, 一般使用单通道的音频数据.
>
> 采样深度: 每次采集声音的数据范围. 16位采样深度一般表示一次采集16位有符号整数大小的数据.采样深度越大, 越容易采集到声音的细微变化.

```python
from maix import nn, audio

# Only MaixCAM2 supports this model.
sample_rate = 44100
p = audio.Player(sample_rate=sample_rate)
p.volume(80)

melotts = nn.MeloTTS(model="/root/models/melotts/melotts-zh.mud", speed = 0.8, language='zh')

pcm = melotts.infer('你好', output_pcm=True)
p.play(pcm)
```


注：
1. 首先需要导入nn模块才能创建MelloTTS模型对象
```python
from maix import nn
```
2. 选择需要加载的模型，目前支持`melotts-zh`模型
   - speed用来设置播放的语速
   - language用来设置语言类型
```python
melotts = nn.MeloTTS(model="/root/models/melotts/melotts-zh.mud", speed = 0.8, language='zh')
```
3. 开始推理
   - 这里推理的文本为'你好'
   - 将output_pcm设置为True来返回pcm数据
```python
pcm = melotts.infer('你好', output_pcm=True)
```
4. 使用音频播放模块来播放刚才生成的音频
   - 注意采样率要设置为与模型输出的采样率一致
   - 把使用`p.volume(80)`来控制输出的音量, 范围为[0, 100]
   - 使用`p.play(pcm)`开始播放由MeloTTS生成的pcm
```shell
p = audio.Player(sample_rate=sample_rate)
p.volume(80)
p.play(pcm)
```
