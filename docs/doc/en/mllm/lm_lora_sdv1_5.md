---
title: Running the LCM-LoRA-SDv1-5 Model on MaixPy MaixCAM
update:
  - date: 2025-12-03
    author: lxowalle
    version: 1.0.0
    content: Added LCM-LoRA-SDv1-5 code and documentation
---

## Supported Devices

| Device      | Supported |
| -------- | ------- |
| MaixCAM2 | ✅ |
| MaixCAM  | ❌ |


## Introduction to the LCM-LoRA-SDv1-5 Model

LCM-LoRA-SDv1-5 is a model that supports text-to-image and image-to-image generation, based on the StableDiffusion 1.5 LCM project. With this model, you can generate conceptual images for artistic creation—simply provide a text description, and the model will generate an image based on it.

## Running the LCM-LoRA-SDv1-5 Model on MaixPy MaixCAM

### Model and Download Link

If the `LCM-LoRA-SDv1-5` model is not present in the system directory `/root/models` by default, you need to download it manually.

 * Memory requirement: CMM memory 1 GiB. For details, refer to the [Memory Usage Documentation](../pro/memory.md)

 * Download link: https://huggingface.co/sipeed/lcm-lora-sdv1-5-maixcam2

For the download method, refer to the instructions in the [Qwen documentation](../pro/memory.md)

### Running the Model

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


