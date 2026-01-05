---
title: MaixPy MaixCAM 大模型使用说明
update:
  - date: 2026-01-05
    author: lxowalle
    version: 1.0.0
    content: 新增大模型使用说明文档
---

## 简介

这篇文章档主要概括性的介绍如何获取和使用大模型，包括文生图、图生图、语音转文本、文本转语音、聊天等模型

大模型支持列表:

| 已支持的模型                                                 | 已支持的平台 | 内存需求 | 说明           |
| ------------------------------------------------------------ | ------------ | -------- | -------------- |
| [lcm-lora-sdv1-5-maixcam2](./dlm_lora_sdv1_5.md)             | MaixCAM2     | 4G       | 文生图/图生图 |
| [lcm-lora-sdv1-5-320x320-maixcam2](./dlm_lora_sdv1_5.md)     | MaixCAM2     | 4G       | 文生图/图生图 |
| [sensevoice-maixcam2](./asr_sensevoice.md)                   | MaixCAM2     | 1G       | 语音转文字     |
| [whisper-basic-maixcam2](asr_whisper.md)                           | MaixCAM2     | 1G       | 语音转文字     |
| [melotts-maixcam2](tts_melotts.md)                           | MaixCAM2     | 1G       | 文字转语音     |
| [smolvlm-256m-instruct-maixcam2](vlm_smolvlm.md)             | MaixCAM2     | 1G       | 视觉语言模型   |
| [InternVL2.5-1B-maixcam2](vlm_internvl.md)                   | MaixCAM2     | 4G       | 视觉语言模型   |
| [ Qwen3-VL-2B-Instruct-GPTQ-Int4-AX630C-P320-CTX448-maixcam2](vlm_qwen3.md) | MaixCAM2     | 4G       | 视觉语言模型   |
| [deepseek-r1-distill-qwen-1.5B-maixcam2](llm_deepseek.md)    | MaixCAM2     | 4G       | 语言模型       |
| [Qwen2.5-1.5B-Instruct-maixcam2](llm_qwen.md)                | MaixCAM2     | 4G       | 语言模型       |
| [Qwen2.5-0.5B-Instruct-maixcam2](llm_qwen.md)                | MaixCAM2     | 4G       | 语言模型       |

## 下载方法

目前提供了`云盘下载`和从`HuggingFace`下载两种方法

### 网盘下载

[下载镜像(百度网盘)](https://pan.baidu.com/s/1r4ECNlaTVxhWIafNBZOztg) 提取码:`vjex`

[下载镜像(MEGA)](https://mega.nz/folder/01IEDZQb#3ktByGkFMn_x6jDxMLbK4w)

在上面`大模型支持列表`中找到需要的模型，从网盘中找到对应的模型并下载. 以`lcm-lora-sdv1-5-maixcam2`模型为例，找到类似`lcm-lora-sdv1-5-maixcam2-202601051759.zip`的文件并下载， 后缀`202601051759`是打包模型的时间。

### HuggingFace下载

> 注：
>
> 1. 从HuggingFace下载对网络环境有要求， 如果网络环境较差可能会出现中途下载失败的情况
> 2. 下面的方法也可以到目标平台（例如MaixCAM2））的终端里执行

1. 命令行下载

   安装下载工具

   ```shell
   pip install huggingface_hub
   ```

   设置下载源，默认是`https://huggingface.co`，对于中国区域可以修改为`https://hf-mirror.com`

   ```shell
   # Linux/MacOS
   export HF_ENDPOINT=https://hf-mirror.com # or 'https://huggingface.co'
   
   # Windows
   ## cmd终端
   set HF_ENDPOINT=https://hf-mirror.com
   ## PowerShell
   $env:HF_ENDPOINT = "https://hf-mirror.com"
   ```

   从`HuggingFace`下载`lcm-lora-sdv1-5-maixcam2`模型的示例，如果需要下载其他模型， 则将`lcm-lora-sdv1-5-maixcam2`修改为需要下载的模型名称。

   ```shell
   # 下载模型(新)
   hf download sipeed/lcm-lora-sdv1-5-maixcam2 --local-dir /root/models
   
   # 下载模型(旧)
   huggingface-cli download sipeed/lcm-lora-sdv1-5-maixcam2 --local-dir /root/models
   ```

2. 使用Python下载

   安装`huggingface_hub`包

   ```python
   pip install huggingface_hub
   ```

   从`HuggingFace`下载`lcm-lora-sdv1-5-maixcam2`模型的示例，如果需要下载其他模型， 则将`model_name`修改为需要下载的模型名称。

   ```python
   # This scripy is used to install models from huggingface
   # Only support MaixCAM2 platform
   
   import os
   os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com' # or 'https://huggingface.co'
   
   from huggingface_hub import snapshot_download
   from huggingface_hub.utils import tqdm
   
   CAPTURE_PROGRESS=False
   class Tqdm(tqdm):
       def __init__(self, *args, **kwargs):
           super().__init__(*args, **kwargs)
           if CAPTURE_PROGRESS:
               print(f"[INIT] {self.desc} | {self.n}/{self.total} ({self.n/self.total*100:.2f}%)")
           else:
               print('')
               
       def update(self, n=1):
           super().update(n)
           if CAPTURE_PROGRESS:
               print(f"[UPDATE] {self.desc} | {self.n}/{self.total} ({self.n/self.total*100:.2f}%)")
           else:
               print('')
       
       def close(self):
           super().close()
           if CAPTURE_PROGRESS:
               print(f"[CLOSE] {self.desc} | {self.n}/{self.total} ({self.n/self.total*100:.2f}%)")
           else:
               print('')
   
   model_name = 'lcm-lora-sdv1-5-maixcam2'
   repo_id = f'sipeed/{model_name}'
   local_dir = f'/root/models/{model_name}'
   snapshot_download(
       repo_id=repo_id,
       local_dir=local_dir,
       # allow_patterns="*.py",
       tqdm_class=Tqdm,
   )
   ```


## 上传模型到板子

下载完成后可以通过`scp`命令将模型上传到板子中， 一般建议上传到`/root/models`目录下。

以`lcm-lora-sdv1-5-maixcam2`模型为例：

1. 确认需要上传的文件

   `lcm-lora-sdv1-5-maixcam2`模型的目录为:

   ```shell
   lcm-lora-sdv1-5-maixcam2
   ├── lcm-lora-sdv1-5-maixcam2					# 实际需要上传的模型文件
   ├── README.md
   ├── README_ZH.md
   └── launcher.py
   ```

   父目录`lcm-lora-sdv1-5-maixcam2`下的文件夹`lcm-lora-sdv1-5-maixcam2`是需要上传的模型文件夹, 注意一定要上传整个模型文件夹

2. 上传模型到开发板

   使用`scp`命令上传`lcm-lora-sdv1-5-maixcam2`模型到板子的示例(假设板子的IP是：`192.168.10.100`):

   > 注：
   >
   > 1. 建议通过USB网口上传模型， 速度更快。USB网口IP的获取方法见[有线连接](../README_MaixCAM2.md###准备连接电脑和设备)

   ```shell
   scp -r lcm-lora-sdv1-5-maixcam2/lcm-lora-sdv1-5-maixcam2 root@192.168.10.100:/root/models
   ```

## 使用模型

使用对应模型的方法请参考对应文档，例如参考[Qwen 大语言模型](./llm_qwen.md)， [InternVL 视觉语言模型](./vlm_internvl.md)，[SmolVLM 视觉语言模型](./vlm_smolvlm.md)
