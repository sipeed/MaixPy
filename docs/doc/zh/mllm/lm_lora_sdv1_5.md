---
title: MaixPy MaixCAM 运行 LCM-LoRA-SDv1-5 模型
update:
  - date: 2025-12-03
    author: lxowalle
    version: 1.0.0
    content: 新增 LCM-LoRA-SDv1-5 代码和文档
---

## 支持的设备

| 设备      | 是否支持 |
| -------- | ------- |
| MaixCAM2 | ✅ |
| MaixCAM  | ❌ |


## LCM-LoRA-SDv1-5 模型简介

LCM-LoRA-SDv1-5 是一个支持文生图, 图生图的模型, 基于 StableDiffusion 1.5 LCM 项目. 我们可以通过这个模型来生成艺术创作的概念图, 只需要输入一段图片的描述文字, 模型便可以基于描述生成一张图片.

## 在 MaixPy MaixCAM 运行 LCM-LoRA-SDv1-5 模型

### 模型和下载地址

默认系统`/root/models`目录下如果没有`LCM-LoRA-SDv1-5`模型，需要自行下载。

  * 内存需求：CMM 内存 1GiB，内存解释请看[内存使用文档](../pro/memory.md)
  * 下载地址：https://huggingface.co/sipeed/lcm-lora-sdv1-5-maixcam2

下载方法参考[Qwen 文档](./llm_qwen.md) 里面的下载方法。

### 运行模型

请参考模型文件中的`launcher.py`来运行模型.

#### 文生图
```shell
cd lcm-lora-sdv1-5-maixcam2
python3 launcher.py --isize 256 --model_dir ax620e_models/ -o "ax620e_txt2img_axe.png" --prompt "a white dog"
```

参数说明:
- `--isize`: 输入图片的尺寸, 推荐填写256
- `--model_dir`: 模型目录
- `-o`: 输出图片名称
- `--prompt`: 描述文字, 模型基于这里的描述生成图片

#### 图生图
```shell
cd lcm-lora-sdv1-5-maixcam2
python3 launcher.py --init_image ax620e_models/img2img-init.png --isize 256 --model_dir ax620e_models/ --seed 1 --prompt "Change to black clothes" -o "ax620e_img2img_axe.png"
```

参数说明:
- `--init_image`: 初始图片, 模型基于这个图片生成图片
- `--isize`: 输入图片的尺寸, 推荐填写256
- `--model_dir`: 模型目录
- `--seed`: 随机种子, 代表图片生成时的随机性
- `-o`: 输出图片名称
- `--prompt`: 描述文字, 模型基于这里的描述生成图片


