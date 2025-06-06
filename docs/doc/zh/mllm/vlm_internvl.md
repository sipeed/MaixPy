---
title: MaixPy MaixCAM 运行 VLM InternVL 视觉语言模型
update:
  - date: 2025-06-05
    author: neucrack
    version: 1.0.0
    content: 新增 InternVL 代码和文档
---

## 支持的设备

| 设备      | 是否支持 |
| -------- | ------- |
| MaixCAM2 | ✅ |
| MaixCAM  | ❌ |


## InternVL 简介

VLM(Vision-Language Model) 即视觉语言模型，可以通过文字+图像输入，让 AI 输出文字，比如让 AI 描述图像中的内容，即 AI 学会了看图。
InternVL 支持多种语言，比如中文和英文。

MaixPy 中移植了 [InternVL2.5](https://huggingface.co/OpenGVLab/InternVL2_5-1B)，其底层基于 Qwen2.5 增加了图像的支持，所以一些基础概念这里不详细介绍，建议先看[Qwen](./llm_qwen.md) 的介绍。

比如这里这张图片，输入系统提示词`你是由上海人工智能实验室联合商汤科技开发的书生多模态大模型，英文名叫InternVL, 是一个有用无害的人工智能助手。` + 用户提示词`请描述图中有什么`，在 MaixCAM2 中使用 InternVL2.5-1B 的结果（也是下文代码的结果）：
![ssd_car.jpg](../../assets/ssd_car.jpg)

```
>> 请描述图中有什么
图中有一个红色双层巴士停在马路上，前面是一辆黑色的小轿车。一位穿黑色夹克的人站在巴士前面，脸上带着微笑。背景是城市建筑，有商店和多幅广告牌。路上的画面上有一个行人图案。

>> Describe the picture
In the image, we see a vibrant street scene featuring a classic double-decker bus in red with "Things Get New Look!" written on its side. It’s parked on the street, where a woman stands smiling at the camera. Behind the bus, a row of classic buildings with large windows lines the street, contributing to the urban atmosphere. A black van is parked nearby, and there are a few people and street signs indicating traffic regulations. The overall scene captures a typical day in a historic city.
```

这里是随便设置的提示词的效果，可以根据实际情况，调整系统提示词和用户提示词。


## MaixPy MaixCAM 中使用 InternVL

### 模型和下载地址

MaixPy 目前支持 InternVL2.5，默认系统`/root/models`目录下已经有`1B`的模型了，如果没有，可以自行下载。
* **1B**:
  * 内存需求： CMM 内存 1GiB，内存解释请看[内存使用文档](../pro/memory.md)
  * 下载地址： https://huggingface.co/sipeed/InternVL2.5-1B-maixcam2

### 下载方法

先保证下载工具安装好：
```
pip install huggingface_hub
```
中国国内可以
```
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple huggingface_hub
```

如果是中国国内，可以先设置国内镜像，下载速度会更快：
Linux/MacOS:
```
export HF_ENDPOINT=https://hf-mirror.com
```
Windows:
CMD终端： `set HF_ENDPOINT=https://hf-mirror.com`
PowerShell: `$env:HF_ENDPOINT = "https://hf-mirror.com"`


然后下载：

```shell
huggingface-cli download sipeed/InternVL2.5-1B-maixcam2--local-dir InternVL2.5-1B-maixcam2
```

### 运行模型

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

internvl.set_system_prompt("你是由上海人工智能实验室联合商汤科技开发的书生多模态大模型，英文名叫InternVL, 是一个有用无害的人工智能助手。")
internvl.set_reply_callback(on_reply)

# load and set image
img = image.load("/maixapp/share/picture/2024.1.1/ssd_car.jpg", format=in_fmt)
internvl.set_image(img, fit=image.Fit.FIT_CONTAIN) # if size not math, will auto resize first
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

结果：
```
>> 请描述图中有什么
图中有一个红色双层巴士停在马路上，前面是一辆黑色的小轿车。一位穿黑色夹克的人站在巴士前面，脸上带着微笑。背景是城市建筑，有商店和多幅广告牌。路上的画面上有一个行人图案。

>> Describe the picture
In the image, we see a vibrant street scene featuring a classic double-decker bus in red with "Things Get New Look!" written on its side. It’s parked on the street, where a woman stands smiling at the camera. Behind the bus, a row of classic buildings with large windows lines the street, contributing to the urban atmosphere. A black van is parked nearby, and there are a few people and street signs indicating traffic regulations. The overall scene captures a typical day in a historic city.
```

这里从系统加载了一张图片，并且让它描述图中有什么，注意这个模型是**不支持上下文**的，也就是说每次调用`send`函数都是全新的对话，不会记住之前`send`的内容。

另外，默认模型支持`364 x 364`的图片输入分辨率，所以调用`set_image`时，如果分辨率不是这个分辨率，会自动调用`img.resize`方法进行缩放，缩放方法为`fit`指定的方法，比如`image.Fit.FIT_CONTAIN`就是当输入图片分辨率和期望的分辨率比例不一致时采用保持原比例缩放，周围空白填充黑色。


`set_system_prompt` 是系统提示语句，可以适当进行修改来提高你的应用场景的准确率。

注意发送的文字编码成 token 后的长度是有限制的，比如默认提供的 1B 模型 是 256 个 token，以及发送+回复最多 1023 个 token。

### 修改参数

模型有一些参数可以修改，参考[Qwen 文档](./llm_qwen.md)。


## 自定义量化模型

上面提供的模型是为 MaixCAM2 量化后的模型，如果需要自己量化模型，可以参考：
* [pulsar2文档](https://pulsar2-docs.readthedocs.io/zh-cn/latest/appendix/build_llm.html)
* 原始模型： https://huggingface.co/OpenGVLab/InternVL2_5-1B
* 更多文章： https://zhuanlan.zhihu.com/p/4118849355
