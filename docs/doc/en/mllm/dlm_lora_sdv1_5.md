---
title: Running the LCM-LoRA-SDv1-5 Model on MaixPy MaixCAM
update:
  - date: 2025-12-03
    author: lxowalle
    version: 1.0.0
    content: Added LCM-LoRA-SDv1-5 code and documentation
---

## Introduction to the LCM-LoRA-SDv1-5 Model

LCM-LoRA-SDv1-5 is a model that supports text-to-image and image-to-image generation, based on the StableDiffusion 1.5 LCM project. With this model, you can generate conceptual images for artistic creation—simply provide a text description, and the model will generate an image based on it.

## Downloading the Model

Supported models:

| Model                                                         | Platform     | Memory Requirement | Description              |
| ------------------------------------------------------------ | -------- | -------- | ----------------- |
| [lcm-lora-sdv1-5-maixcam2](https://huggingface.co/sipeed/lcm-lora-sdv1-5-maixcam2) | MaixCAM2 | 4G       | Output 256x256 resolution |
| [lcm-lora-sdv1-5-320x320-maixcam2](https://huggingface.co/sipeed/lcm-lora-sdv1-5-320x320-maixcam2) | MaixCAM2 | 4G       | Output 320x320 resolution |

Refer to the [Large Model User Guide](./basic.md) to download the model.

### Running the Model with MaixPy

> Note: MaixPy version `4.12.3` or above is required for support.

This example demonstrates how to use MaixPy to run the LCM-LoRA-SDv1-5 model for both text-to-image and image-to-image generation.

```python
from maix import sdv1_5

model = sdv1_5.SDV1_5("/root/models/lcm-lora-sdv1-5-maixcam2/ax620e_models")
model.init(img2img=True)
model.refer(prompt="A white dog.", save_path="/root/text2img.jpg")
model.refer(prompt="Replace the dog with a cat.", init_image_path="/root/text2img.jpg", seed=1, save_path="/root/img2img.jpg")

model.deinit()
```
Output:
![](../../assets/ldm_sdv1.5_img2img.jpg)

Explanation:
1. When performing text-to-image generation, you need to define a `prompt` describing the image you want. The prompt must be written in English, and the generated image will be saved to the path specified by `save_path`.
2. When performing image-to-image generation, you need to define a prompt describing the content you want to generate`init_image_path` specifies the initial image,`seed` controls randomness in image generation
The output image will be saved to the path specified by save_path.
3. Since `sdv1_5` depends on several large Python packages, importing it may take some time. If you want the application to enter the UI quickly during development, you can use `importlib` and `threading` to load the module in the background. Example:
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

### Running the Model with Command Line

Refer to `launcher.py` in the model directory to run the model.

#### Text-to-Image
```shell
cd lcm-lora-sdv1-5-maixcam2
python3 launcher.py --isize 256 --model_dir ax620e_models/ -o "ax620e_txt2img_axe.png" --prompt "a white dog"
```

Parameter description:
- `--isize`: Input image size, recommended value is 256
- `--model_dir`: Model directory
- `-o`: Output image filename
- `--prompt`: Description text; the model generates an image based on this description

#### Image-to-Image
```shell
cd lcm-lora-sdv1-5-maixcam2
python3 launcher.py --init_image ax620e_models/img2img-init.png --isize 256 --model_dir ax620e_models/ --seed 1 --prompt "Change to black clothes" -o "ax620e_img2img_axe.png"
```

Parameter description:
- `--init_image`: Initial image; the model generates a new image based on this
- `--isize`: Input image size, recommended value is 256
- `--model_dir`: Model directory
- `--seed`: Random seed, controls randomness during image generation
- `-o`: Output image filename
- `--prompt`: Description text; the model generates an image based on this description


