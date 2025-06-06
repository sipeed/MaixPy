---
title: MaixPy MaixCAM Running VLM InternVL Vision-Language Model
update:
  - date: 2025-06-05
    author: neucrack
    version: 1.0.0
    content: Added InternVL code and documentation
---

## Supported Devices

| Device   | Supported |
| -------- | --------- |
| MaixCAM2 | ✅         |
| MaixCAM  | ❌         |

## Introduction to InternVL

VLM (Vision-Language Model) refers to a vision-language model that allows AI to generate text output based on both text and image input, such as describing the content of an image, meaning the AI has learned to interpret images.
InternVL supports multiple languages, such as Chinese and English.


MaixPy has integrated [InternVL2.5](https://huggingface.co/OpenGVLab/InternVL2_5-1B), which is based on Qwen2.5 with added image support. Therefore, some basic concepts are not detailed here. It is recommended to read the [Qwen](./llm_qwen.md) introduction first.


For example, with this image, using the system prompt
`你是由上海人工智能实验室联合商汤科技开发的书生多模态大模型，英文名叫InternVL, 是一个有用无害的人工智能助手。`
and the user prompt
`Describe the picture`
on MaixCAM2 with InternVL2.5-1B (which is also the result of the code below):
![ssd\_car.jpg](../../assets/ssd_car.jpg)
```
>> 请描述图中有什么
图中有一个红色双层巴士停在马路上，前面是一辆黑色的小轿车。一位穿黑色夹克的人站在巴士前面，脸上带着微笑。背景是城市建筑，有商店和多幅广告牌。路上的画面上有一个行人图案。

>> Describe the picture
In the image, we see a vibrant street scene featuring a classic double-decker bus in red with "Things Get New Look!" written on its side. It’s parked on the street, where a woman stands smiling at the camera. Behind the bus, a row of classic buildings with large windows lines the street, contributing to the urban atmosphere. A black van is parked nearby, and there are a few people and street signs indicating traffic regulations. The overall scene captures a typical day in a historic city.
```
This is the result with a casually set prompt. You can adjust the system and user prompts according to the actual situation.


## Using InternVL in MaixPy MaixCAM

### Model and Download Link

MaixPy currently supports InternVL2.5. By default, a `1B` model is already available under the `/root/models` directory of the system. If not, you can download it manually.

* **1B**:

  * Memory requirement: CMM memory 1GiB. For details, see the [Memory Usage Documentation](../pro/memory.md)
  * Download link: [https://huggingface.co/sipeed/InternVL2.5-1B-maixcam2](https://huggingface.co/sipeed/InternVL2.5-1B-maixcam2)

### Download Method

Make sure the download tool is installed:

```
pip install huggingface_hub
```

Within China, you can use:

```
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple huggingface_hub
```

If you are in China, you can set a domestic mirror to speed up the download:
Linux/MacOS:

```
export HF_ENDPOINT=https://hf-mirror.com
```

Windows:
CMD terminal: `set HF_ENDPOINT=https://hf-mirror.com`
PowerShell: `$env:HF_ENDPOINT = "https://hf-mirror.com"`

Then download:

```shell
huggingface-cli download sipeed/InternVL2.5-1B-maixcam2 --local-dir InternVL2.5-1B-maixcam2
```

### Running the Model

```python
from maix import nn, err, log, sys, image, display

model = "/root/models/InternVL2.5-1B/model.mud"
log.set_log_level(log.LogLevel.LEVEL_ERROR, color = False)
disp = display.Display()

def show_mem_info():
    print("memory info:")
    for k, v in sys.memory_info().items():
        print(f"\t{k:12}: {sys.bytes_to_human(v)}")
    print("")

show_mem_info()
internvl = nn.InternVL(model)
show_mem_info()

in_w = internvl.input_width()
in_h = internvl.input_height()
in_fmt = internvl.input_format()
print(f"input size: {in_w}x{in_h}, format: {image.format_name(in_fmt)}")

def on_reply(obj, resp):
    print(resp.msg_new, end="")

internvl.set_system_prompt("You are InternVL, a multimodal large model co-developed by Shanghai AI Laboratory and SenseTime, a helpful and harmless AI assistant.")
internvl.set_reply_callback(on_reply)

# load and set image
img = image.load("/maixapp/share/picture/2024.1.1/ssd_car.jpg", format=in_fmt)
internvl.set_image(img, fit=image.Fit.FIT_CONTAIN) # if size not match, will auto resize first
disp.show(img)

# set prompt
msg = "请描述图中有什么"
print(">>", msg)
resp = internvl.send(msg)
err.check_raise(resp.err_code)

msg = "Describe the picture"
print(">>", msg)
resp = internvl.send(msg)
err.check_raise(resp.err_code)
# print(resp.msg)
```

Result:
```
>> 请描述图中有什么
图中有一个红色双层巴士停在马路上，前面是一辆黑色的小轿车。一位穿黑色夹克的人站在巴士前面，脸上带着微笑。背景是城市建筑，有商店和多幅广告牌。路上的画面上有一个行人图案。

>> Describe the picture
In the image, we see a vibrant street scene featuring a classic double-decker bus in red with "Things Get New Look!" written on its side. It’s parked on the street, where a woman stands smiling at the camera. Behind the bus, a row of classic buildings with large windows lines the street, contributing to the urban atmosphere. A black van is parked nearby, and there are a few people and street signs indicating traffic regulations. The overall scene captures a typical day in a historic city.
```

This loads an image from the system and asks the model to describe what’s in the image. Note that this model **does not support context**, meaning each call to the `send` function is a brand-new conversation and does not remember the content from previous `send` calls.

Additionally, the default model supports image input resolution of `364 x 364`. So when calling `set_image`, if the resolution doesn't match, it will automatically call `img.resize` to resize the image using the method specified by `fit`, such as `image.Fit.FIT_CONTAIN`, which resizes while maintaining the original aspect ratio and fills the surrounding space with black.

`set_system_prompt` is the system prompt and can be modified to improve accuracy in your application scenario.

Note that the length of the input text after being tokenized is limited. For example, the default 1B model supports 256 tokens, and the total tokens for input and output should not exceed 1023.

## Modifying Parameters

Refer to [Qwen Documentation](./llm_qwen.md)。

## Custom Quantized Model

The model provided above is a quantized model for MaixCAM2. If you want to quantize your own model, refer to:

* [Pulsar2 Documentation](https://pulsar2-docs.readthedocs.io/zh-cn/latest/appendix/build_llm.html)
* Original model: https://huggingface.co/OpenGVLab/InternVL2_5-1B
* More articles: [https://zhuanlan.zhihu.com/p/4118849355](https://zhuanlan.zhihu.com/p/4118849355)
