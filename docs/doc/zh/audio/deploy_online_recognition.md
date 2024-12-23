---
title: MaixCAM MaixPy 部署在线语音识别环境
update:
  - date: 2024-12-23
    author: lxowalle
    version: 1.0.0
    content: 初版文档
---

## 简介

本地部署在线语音识别是一种实现语音输入实时处理的解决方案。它通过在本地服务器上运行语音识别模型并与`MaixCAM`交互，无需依赖外部云服务，实现语音数据的即时处理和结果返回。这种方式不仅能够提升响应速度，还能更好地保护用户隐私，特别适用于对数据安全和实时性要求较高的应用场景，如智能硬件、工业控制和实时字幕生成等。

本文选择了开源的[`sherpa-onnx`](https://github.com/k2-fsa/sherpa-onnx)框架进行部署, `sherpa-onnx`框架是`sherpa`的子项目, 支持流式语音识别,非流式语音识别,文本转语音,说话人分类,说话人识别,说话人验证,口语识别等等。下文主要介绍使用`MaixCAM`与`sherpa-onnx`实现流式语音识别.

> 注: 流式语音识别的特点是实时性高,并且可以边说边识别, 常用于实时翻译, 语音助手等场景; 非流式语音识别的特点是必须每次推理完整的一句话,准确度高



## 部署语音识别服务器

`sherpa-onnx`支持非常多的语言部署，包括`C/C++`，`Python`，`Java`等等，为了部署方便，我们选择使用`Python`语言部署。下面操作过程中有任何疑问，可以自己先看一遍`sherpa`的[文档](https://k2-fsa.github.io/sherpa/intro.html)， 下面开始部署吧～

#### 下载`sherpa-onnx`仓库

```shell
git clone https://github.com/k2-fsa/sherpa-onnx.git
```

#### 安装依赖包

```python
pip install numpy
pip install websockets
```

#### 安装sherpa-onnx包

```python
pip install sherpa-onnx
```

如果需要使用`GPU`， 则下载带`cuda`的包

```python
pip install sherpa-onnx==1.10.16+cuda -f https://k2-fsa.github.io/sherpa/onnx/cuda.html

# 中国用户可以使用
# pip install sherpa-onnx==1.10.16+cuda -f https://k2-fsa.github.io/sherpa/onnx/cuda-cn.html
```

如果找不到包或安装失败，可以选择从源码编译安装

```python
cd sherpa-onnx
export SHERPA_ONNX_CMAKE_ARGS="-DSHERPA_ONNX_ENABLE_GPU=ON"
python3 setup.py install
```

如果有`GPU`但是没有`cuda`环境，则点击[`这里`](https://k2-fsa.github.io/k2/installation/cuda-cudnn.html)的方法安装对应版本`cuda`

#### 检查`sherpa-onnx`包是否安装成功

```python
python3 -c "import sherpa_onnx; print(sherpa_onnx.__version__)"

# 输出应该是
# sherpa-onnx 或 1.10.16+cuda
```

#### 下载模型

[`中英文双语zipformer模型 sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20-mobile`](https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/.tar.bz2)

[`中英文双语paraformer模型 sherpa-onnx-streaming-paraformer-trilingual-zh-cantonese-en`](https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-streaming-paraformer-trilingual-zh-cantonese-en.tar.bz2)

> 注：中文识别建议用`sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20-mobile`模型
>
> 英文识别建议用`sherpa-onnx-streaming-paraformer-trilingual-zh-cantonese-en`模型

#### 运行服务器

`sherpa-onnx`提供了一个服务器的示例代码，所以不需要我们再造轮子编代码才能体验在线语音识别，启动方法看下面的示例

##### 运行`zipformer`模型

```shell
cd sherpa-onnx
export MODEL_PATH="sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20"
python3 ./python-api-examples/streaming_server.py \
  --encoder ./${MODEL_PATH}/encoder-epoch-99-avg-1.onnx \
  --decoder ./${MODEL_PATH}/decoder-epoch-99-avg-1.onnx \
  --joiner ./${MODEL_PATH}/joiner-epoch-99-avg-1.onnx \
  --tokens ./${MODEL_PATH}/tokens.txt \
  --provider "cuda"
```

这个示例运行了`streaming_server.py`作为服务器代码，其中`--encoder`、`--decoder`和`--joiner`是模型文件，`--tokens`是用来映射模型输出的列表， `--provider`用来指示是否启用`GPU`，默认使用`CPU`

##### 运行`paraformer`模型

```shell
cd sherpa-onnx
export MODEL_PATH="sherpa-onnx-streaming-paraformer-trilingual-zh-cantonese-en"
python3 ./python-api-examples/streaming_server.py \
  --paraformer-encoder ./${MODEL_PATH}/encoder.onnx \
  --paraformer-decoder ./${MODEL_PATH}/decoder.onnx \
  --tokens ./${MODEL_PATH}/tokens.txt \
  --provider "cuda"

```

这个示例运行了`streaming_server.py`作为服务器代码，其中`--paraformer-encoder`和`--paraformer-encoder`是模型文件，`--tokens`是用来映射模型输出的列表， `--provider`用来指示是否启用`GPU`，默认使用`CPU`

##### 运行成功后的日志

```shell
2024-12-23 09:25:17,557 INFO [streaming_server.py:667] No certificate provided
2024-12-23 09:25:17,561 INFO [server.py:715] server listening on [::]:6006
2024-12-23 09:25:17,561 INFO [server.py:715] server listening on 0.0.0.0:6006
2024-12-23 09:25:17,561 INFO [streaming_server.py:693] Please visit one of the following addresses:

  http://localhost:6006

Since you are not providing a certificate, you cannot use your microphone from within the browser using public IP addresses. Only localhost can be used.You also cannot use 0.0.0.0 or 127.0.0.1
```

至此ASR模型服务器就跑起来了，开始与服务器通信

#### 基于`MaixCAM`与服务器通信

为了简化篇幅这里放了示例客户端代码的链接，自行拷贝。注意大部分情况音频数据要求采样率`16000Hz`， 采样通道为`1`。

`MaixCAM`流式识别点击[这里](https://github.com/sipeed/MaixPy/blob/main/examples/audio/asr/asr_streaming_websockt_client)获取代码

`MaixCAM`非流式识别点击[这里](https://github.com/sipeed/MaixPy/blob/main/examples/audio/asr/asr_non_streaming_websockt_client)获取代码

```shell
# 修改服务器地址
SERVER_ADDR = "127.0.0.1"
SERVER_PORT = 6006
```

修改服务器地址和端口号后，再使用`maixvision`运行即可。如果你运行的是流式识别的代码，那么尝试跟`MaixCAM`开始对话吧～

> 注：这里没有过多赘述客户端和服务器通信的协议的原因之一是因为它们通信很简单，基本是`websocket`连接后的数据裸收发，建议先上手体验后直接看代码来了解真正想知道的信息。

至此就部署完成了
