---
title: MaixPy MaixCAM Large Model User Guide
update:
  - date: 2026-01-05
    author: lxowalle
    version: 1.0.0
    content: Added large model usage documentation
---

## Introduction

This document provides an overview of how to obtain and use large models, including models for text-to-image, image-to-image, speech-to-text, text-to-speech, and chat.

List of supported large models:

| Supported Model                                                 | Supported Platform | Memory Requirement | Description           |
| ------------------------------------------------------------ | ------------ | -------- | -------------- |
| [lcm-lora-sdv1-5-maixcam2](./dlm_lora_sdv1_5.md)             | MaixCAM2     | 4G       | Text-to-Image / Image-to-Image |
| [lcm-lora-sdv1-5-320x320-maixcam2](./dlm_lora_sdv1_5.md)     | MaixCAM2     | 4G       | Text-to-Image / Image-to-Image |
| [sensevoice-maixcam2](./asr_sensevoice.md)                   | MaixCAM2     | 1G       | Speech-to-Text     |
| [whisper-basic-maixcam2](asr_whisper.md)                           | MaixCAM2     | 1G       | Speech-to-Text     |
| [melotts-maixcam2](tts_melotts.md)                           | MaixCAM2     | 1G       | Text-to-Speech     |
| [smolvlm-256m-instruct-maixcam2](vlm_smolvlm.md)             | MaixCAM2     | 1G       | Vision-Language Model   |
| [InternVL2.5-1B-maixcam2](vlm_internvl.md)                   | MaixCAM2     | 4G       | Vision-Language Model   |
| [ Qwen3-VL-2B-Instruct-GPTQ-Int4-AX630C-P320-CTX448-maixcam2](vlm_qwen3.md) | MaixCAM2     | 4G       | Vision-Language Model   |
| [deepseek-r1-distill-qwen-1.5B-maixcam2](llm_deepseek.md)    | MaixCAM2     | 4G       | Language Model       |
| [Qwen2.5-1.5B-Instruct-maixcam2](llm_qwen.md)                | MaixCAM2     | 4G       | Language Model       |
| [Qwen2.5-0.5B-Instruct-maixcam2](llm_qwen.md)                | MaixCAM2     | 4G       | Language Model       |

## Download Methods

Currently, two download methods are provided: `cloud storage download` and `HuggingFace download`.

### Cloud Storage Download

[Download Images (Baidu Netdisk)](https://pan.baidu.com/s/1r4ECNlaTVxhWIafNBZOztg) Extraction code:`vjex`

[Download Images (MEGA)](https://mega.nz/folder/01IEDZQb#3ktByGkFMn_x6jDxMLbK4w)

From the `List of supported large models` above, locate the required model and download it from the cloud storage.
For example, for the `lcm-lora-sdv1-5-maixcam2` model, download a file similar to `lcm-lora-sdv1-5-maixcam2-202601051759.zip`, The suffix `202601051759` indicates the model packaging time.

### HuggingFace Download

> 注：
>
> 1. Downloading from HuggingFace requires a stable network environment. Poor connectivity may result in interrupted downloads
> 2. The following methods can also be executed directly in the terminal of the target platform (e.g., MaixCAM2).

1. Download via Command Line

   Install the download tool:

   ```shell
   pip install huggingface_hub
   ```

   Set the download endpoint. The default is `https://huggingface.co`
   For users in China, it is recommended to use `https://hf-mirror.com`

   ```shell
   # Linux/MacOS
   export HF_ENDPOINT=https://hf-mirror.com # or 'https://huggingface.co'
   
   # Windows
   ## cmd
   set HF_ENDPOINT=https://hf-mirror.com
   ## PowerShell
   $env:HF_ENDPOINT = "https://hf-mirror.com"
   ```

   Example for downloading the `lcm-lora-sdv1-5-maixcam2` model.
   To download another model, replace `lcm-lora-sdv1-5-maixcam2` with the desired model name.
   ```shell
   # Download model (new)
   hf download sipeed/lcm-lora-sdv1-5-maixcam2 --local-dir /root/models
   
   # Download model (legacy)
   huggingface-cli download sipeed/lcm-lora-sdv1-5-maixcam2 --local-dir /root/models
   ```

2. Download Using Python

   Install the `huggingface_hub` package:

   ```python
   pip install huggingface_hub
   ```
   Example for downloading the `lcm-lora-sdv1-5-maixcam2` model. To download other models, replace the `model_name` variable accordingly.

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


## Uploading Models to the Board

After downloading, you can upload the model to the board using the `scp` command. It is recommended to upload models to the `/root/models` directory.

Using `lcm-lora-sdv1-5-maixcam2` as an example:

1. Confirm the Files to Upload

   The directory structure of the `lcm-lora-sdv1-5-maixcam2` model is:

   ```shell
   lcm-lora-sdv1-5-maixcam2
   ├── lcm-lora-sdv1-5-maixcam2					# The actual model files to upload
   ├── README.md
   ├── README_ZH.md
   └── launcher.py
   ```

   The folder `lcm-lora-sdv1-5-maixcam2` under the parent directory is the actual model directory that must be uploaded. Make sure to upload the entire model directory.

2. Upload the Model to the Development Board

   Example of uploading the `lcm-lora-sdv1-5-maixcam2` model to the board using `scp`(assuming the board IP address is 192.168.10.100):

   > Notes:
   >
   > 1. It is recommended to upload models via the USB network interface for higher transfer speed. For details on obtaining the USB network IP address, see[Wired Connection](../README_MaixCAM2.md)

   ```shell
   scp -r lcm-lora-sdv1-5-maixcam2/lcm-lora-sdv1-5-maixcam2 root@192.168.10.100:/root/models
   ```

## Using the Models

For instructions on how to use each model, please refer to the corresponding documentation, for example:
[Qwen Large Language Model](./llm_qwen.md)
[InternVL Vision-Language Model](./vlm_internvl.md)
[SmolVLM Vision-Language Model](./vlm_smolvlm.md)
