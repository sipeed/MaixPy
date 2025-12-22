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

MaixPy 目前支持 `LCM-LoRA-SDv1-5`，由于模型较大, 需要自行下载模型并保存到`/root/models`目录下。
> !!! 注意 !!! 注意 !!! 模型一定要保存到`/root/models`目录下，否则一些应用可能无法加载模型. 例如保存路径为`/root/models/lcm-lora-sdv1-5-maixcam2`

  * 内存需求：CMM 内存 1GiB，内存解释请看[内存使用文档](../pro/memory.md)
  * 下载地址：https://huggingface.co/sipeed/lcm-lora-sdv1-5-maixcam2

下载方法参考[Qwen 文档](./llm_qwen.md) 里面的下载方法。

### MaixPy 运行模型

> 注意:必须要`MaixPy 4.12.3`以上版本才支持

这里的示例展示了如何使用 MaixPy 运行 LCM-LoRA-SDv1-5 模型来实现文生文和图生图的功能

```python
from maix import sdv1_5

model = sdv1_5.SDV1_5("/root/models/lcm-lora-sdv1-5-maixcam2/ax620e_models")
model.init(img2img=True)
model.refer(prompt="A white dog.", save_path="/root/text2img.jpg")
model.refer(prompt="Replace the dog with a cat.", init_image_path="/root/text2img.jpg", seed=1, save_path="/root/img2img.jpg")

model.deinit()
```
输出:
![](../../assets/ldm_sdv1.5_img2img.jpg)

说明:
1. 执行文生文功能时, 需要定义一个`prompt`, 描述你的图片内容, 必须是英文输入, 生成的图片会保存在`save_path`指定的路径
2. 执行图生图功能时, 需要定义一个`prompt`, 描述你要生成图片的内容, `init_image_path`指定初始图片, `seed`指定图片生成时的随机性, 生成的图片会保存在`save_path`指定的路径
3. 由于`sdv1_5`依赖了一些比较大的python包, 因此在导入时会比较慢, 需要耐心等待. 开发时如果希望快速进入界面, 可以尝试使用`importlib`和`threading`库将加载模块的过程放到后台执行, 参考代码:
```python
from maix import time
import importlib, threading

class ModuleLoader():
    def __load_module(self):
        self.module = importlib.import_module(self.module_name)
        self.load_ok = True
        pass
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.module = None
        self.load_ok = False
        self.t = threading.Thread(target=self.__load_module)
        self.t.start()
    def try_get_module(self, block = True):
        if self.load_ok:
            return self.module
        if block:
            while not self.load_ok:
                time.sleep_ms(100)
            return self.module
        else:
            return None

sdv1_5_loader = ModuleLoader("maix.sdv1_5")
while True:
    sdv1_5 = sdv1_5_loader.try_get_module(block=False)
    if sdv1_5 is not None:
        break
    time.sleep_ms(1000)
print(sdv1_5)
```

### 命令行运行模型

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


