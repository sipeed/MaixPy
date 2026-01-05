---
title: MaixPy MaixCAM 运行 SmolVLM 视觉语言模型
update:
  - date: 2025-12-03
    author: lxowalle
    version: 1.0.0
    content: 新增 SmolVLM 代码和文档
---


## SmolVLM 简介

VLM(Vision-Language Model) 即视觉语言模型，可以通过文字+图像输入，让 AI 输出文字，比如让 AI 描述图像中的内容，即 AI 学会了看图。 SmolVLM 目前只支持英文。

## 下载模型

支持列表：

| 模型                                                         | 平台     | 内存需求 | 说明 |
| ------------------------------------------------------------ | -------- | -------- | ---- |
| [smolvlm-256m-instruct-maixcam2](https://huggingface.co/sipeed/smolvlm-256m-instruct-maixcam2) | MaixCAM2 | 1G       |      |

参考[大模型使用说明](./basic.md)下载模型

## MaixPy 使用 SmolVLM

```python
from maix import nn, err, log, sys, image, display

model = "/root/models/smolvlm-256m-instruct-maixcam2/model.mud"
log.set_log_level(log.LogLevel.LEVEL_ERROR, color = False)
disp = display.Display()

smolvlm = nn.SmolVLM(model)
in_w = smolvlm.input_width()
in_h = smolvlm.input_height()
in_fmt = smolvlm.input_format()
print(f"input size: {in_w}x{in_h}, format: {image.format_name(in_fmt)}")

def on_reply(obj, resp):
    print(resp.msg_new, end="")

smolvlm.set_system_prompt("Your a helpful assistant.")
smolvlm.set_reply_callback(on_reply)

# load and set image
img = image.load("/maixapp/share/picture/2024.1.1/ssd_car.jpg", format=in_fmt)
smolvlm.set_image(img, fit=image.Fit.FIT_CONTAIN) # if size not math, will auto resize first
disp.show(img)

msg = "Describe the picture"
print(">>", msg)
resp = smolvlm.send(msg)
err.check_raise(resp.err_code)
```

结果：
```
>> Describe the picture
The image depicts a prominent bus stop, specifically in the middle, where a young woman is captured and standing on the sidewalk. The bus, which appears to be a double-decker bus, is prominently displayed in the center of the image. The bus is red with bold white text and design elements on its side. The text on the bus reads "THING'S GET MORE EXCITING."

Below this text is a small image of the bus logo. The bus is parked next to another bus, both in a city background. The background on which the bus is parked is not clearly discernible due to the perspective, but it looks urban due to the buildings and street signs visible.

The woman in the image is looking towards the bus on the street, possibly waiting to board or simply admiring the scene. She is wearing a black coat, and her hair is short and dark. The bus itself has a red roof, and its windows are visible. The bus’s front is also visible, but it is not as prominent as the bus’s front side.

In the background, there are buildings and a large glass window. The sky is not visible, but it is bright, as indicated by the light reflection on the windows. The street is wide and seems to be a busy urban street, possibly with cars and other vehicles.

The bus stop itself seems to be in an area that is busy. There are traffic signs visible, and the sidewalk looks well-maintained. The street is wide enough for a bus to pass by at a distance, though it is not very wide. The overall environment appears modern and functional.

This vivid depiction of the bus stop and the surrounding environment provides a clear and detailed view of the scene.
```

另外，默认模型支持`512x512`的图片输入分辨率，所以调用`set_image`时，如果分辨率不是这个分辨率，会自动调用`img.resize`方法进行缩放，缩放方法为`fit`指定的方法，比如`image.Fit.FIT_CONTAIN`就是当输入图片分辨率和期望的分辨率比例不一致时采用保持原比例缩放，周围空白填充黑色。

### 修改参数

模型有一些参数可以修改，参考[Qwen 文档](./llm_qwen.md)。

## 自定义量化模型

上面提供的模型是为 MaixCAM2 量化后的模型，如果需要自己量化模型，可以参考：
* [pulsar2文档](https://pulsar2-docs.readthedocs.io/zh-cn/latest/appendix/build_llm.html)
* 原始模型： https://huggingface.co/HuggingFaceTB/SmolVLM-256M-Instruct
