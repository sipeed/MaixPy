---
title: MaixCAM MaixPy Deploy online speech recognition
update:
  - date: 2024-12-23
    author: lxowalle
    version: 1.0.0
    content: Initial document
---

## Introduction

Deploying online speech recognition locally is a solution for real-time processing of speech input. By running a speech recognition model on a local server and interacting with `MaixCAM`, it enables instant processing and result return of audio data without relying on external cloud services. This approach not only improves response speed but also protects user privacy, making it ideal for applications requiring high data security and real-time performance, such as smart hardware, industrial control, and real-time subtitle generation.

This document uses the open-source framework [`sherpa-onnx`](https://github.com/k2-fsa/sherpa-onnx) for deployment. `sherpa-onnx` is a subproject of `sherpa`, supporting various tasks like streaming and non-streaming speech recognition, text-to-speech, speaker classification, speaker recognition, speaker verification, and spoken language recognition. Below, we mainly introduce how to achieve streaming speech recognition using `MaixCAM` and `sherpa-onnx`.

> Note: Streaming speech recognition features high real-time performance, allowing recognition during speech. It is commonly used in real-time translation and voice assistants. Non-streaming recognition requires processing a complete sentence at a time and is known for its high accuracy.

## Deploying the Speech Recognition Server

`sherpa-onnx` supports deployment in multiple languages, including `C/C++`, `Python`, `Java`, and more. For simplicity, we will use `Python` for deployment. If you encounter any issues during the process, you can refer to the `sherpa` [documentation](https://k2-fsa.github.io/sherpa/intro.html). Let's get started!


#### Download the `sherpa-onnx` Repository

```shell
git clone https://github.com/k2-fsa/sherpa-onnx.git
```

#### Install Dependencies

```python
pip install numpy
pip install websockets
```

#### Install the `sherpa-onnx` Package

```python
pip install sherpa-onnx
```

If GPU support is required, install the CUDA-enabled package:

```python
pip install sherpa-onnx==1.10.16+cuda -f https://k2-fsa.github.io/sherpa/onnx/cuda.html

# For users in China
# pip install sherpa-onnx==1.10.16+cuda -f https://k2-fsa.github.io/sherpa/onnx/cuda-cn.html
```

If the package is unavailable or installation fails, build and install from the source:

```python
cd sherpa-onnx
export SHERPA_ONNX_CMAKE_ARGS="-DSHERPA_ONNX_ENABLE_GPU=ON"
python3 setup.py install
```

If a GPU is available but `CUDA` is not installed, refer to the installation guide [`here`](https://k2-fsa.github.io/k2/installation/cuda-cudnn.html)

#### Verify the Installation of `sherpa-onnx`

```python
python3 -c "import sherpa_onnx; print(sherpa_onnx.__version__)"

# Expected output:
# sherpa-onnx or 1.10.16+cuda
```

#### Download the Model

[`Zipformer Bilingual Model for Mandarin and English:sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20-mobile`](https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/.tar.bz2)

[`Paraformer Trilingual Model for Mandarin, Cantonese, and English:sherpa-onnx-streaming-paraformer-trilingual-zh-cantonese-en`](https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-streaming-paraformer-trilingual-zh-cantonese-en.tar.bz2)

> Note：
> For Chinese recognition, it is recommended to use the `sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20-mobile` model
>
> For English recognition, it is recommended to use the `sherpa-onnx-streaming-paraformer-trilingual-zh-cantonese-en` model

#### Run the Server

`sherpa-onnx` provides a server example, so there's no need to write additional code. Follow these steps to start the server.

##### Run the `zipformer` Model

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

##### Run the `paraformer` Model

```shell
cd sherpa-onnx
export MODEL_PATH="sherpa-onnx-streaming-paraformer-trilingual-zh-cantonese-en"
python3 ./python-api-examples/streaming_server.py \
  --paraformer-encoder ./${MODEL_PATH}/encoder.onnx \
  --paraformer-decoder ./${MODEL_PATH}/decoder.onnx \
  --tokens ./${MODEL_PATH}/tokens.txt \
  --provider "cuda"

```

##### Example Log Output

```shell
2024-12-23 09:25:17,557 INFO [streaming_server.py:667] No certificate provided
2024-12-23 09:25:17,561 INFO [server.py:715] server listening on [::]:6006
2024-12-23 09:25:17,561 INFO [server.py:715] server listening on 0.0.0.0:6006
2024-12-23 09:25:17,561 INFO [streaming_server.py:693] Please visit one of the following addresses:

  http://localhost:6006

Since you are not providing a certificate, you cannot use your microphone from within the browser using public IP addresses. Only localhost can be used.You also cannot use 0.0.0.0 or 127.0.0.1
```

At this point, the ASR model server is up and running.

#### Communication Between `MaixCAM` and the Server

For brevity, example client code is provided via the following links. Note that most cases require audio data with a sampling rate of 16000Hz and a single channel:

[`MaixCAMMaixCAM` Streaming Recognition](https://github.com/sipeed/MaixPy/blob/main/examples/audio/asr/asr_streaming_websockt_client)

[`MaixCAM` Non-Streaming Recognition](https://github.com/sipeed/MaixPy/blob/main/examples/audio/asr/asr_non_streaming_websockt_client)

```shell
# Update server address
SERVER_ADDR = "127.0.0.1"
SERVER_PORT = 6006
```

After updating the server address and port, use maixvision to run the client. If using the streaming recognition script, try interacting with MaixCAM.

> Note: This document does not elaborate on the communication protocol because it is straightforward—essentially raw data exchange via WebSocket. It is recommended to first experience the setup and then delve into the code for further details.

The deployment process is now complete.
