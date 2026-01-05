---
title: MaixPy MaixCAM 运行 VLM Qwen3-VL 视觉语言模型
update:
  - date: 2025-11-27
    author: lxowalle
    version: 1.0.0
    content: 新增 Qwen3-VL 代码和文档
---

## Qwen3-VL 简介

Qwen3-VL是Qwen系列的视觉语言模型, 相较上一代版本有更优越的文本理解与生成，更深层次的视觉感知与推理，延长上下文长度，增强空间和视频动态理解，以及更强的代理交互能力.

## 下载模型

支持列表：

| 模型                                                         | 平台     | 内存需求 | 说明              |
| ------------------------------------------------------------ | -------- | -------- | ----------------- |
| [Qwen3-VL-2B-Instruct-GPTQ-Int4-AX630C-P320-CTX448-maixcam2](https://huggingface.co/sipeed/Qwen3-VL-2B-Instruct-GPTQ-Int4-AX630C-P320-CTX448-maixcam2) | MaixCAM2 | 4G     |  |

参考[大模型使用说明](./basic.md)下载模型

## MaixPy 使用 Qwen3-VL

```python
from maix import app, nn, err, image, display, time
import requests
import json

model = "/root/models/Qwen3-VL-2B-Instruct-GPTQ-Int4-AX630C-P320-CTX448-maixcam2/model.mud"
disp = display.Display()

qwen3_vl = nn.Qwen3VL(model)

in_w = qwen3_vl.input_width()
in_h = qwen3_vl.input_height()
in_fmt = qwen3_vl.input_format()
print(f"input size: {in_w}x{in_h}, format: {image.format_name(in_fmt)}")

def on_reply(obj, resp):
    print(resp.msg_new, end="")

qwen3_vl.set_system_prompt("You are Qwen3VL. You are a helpful vision-to-text assistant.")
qwen3_vl.set_reply_callback(on_reply)

# load and set image
img = image.load("/maixapp/share/picture/2024.1.1/ssd_car.jpg", format=in_fmt)
qwen3_vl.set_image(img, fit=image.Fit.FIT_CONTAIN) # if size not math, will auto resize first
disp.show(img)

while not app.need_exit():
    print('wait model is ready')
    if qwen3_vl.is_ready():
        break
    time.sleep(1)

def example1():
    print('')
    # set prompt
    msg = "请描述图中有什么"
    print(">>", msg)
    resp = qwen3_vl.send(msg)
    err.check_raise(resp.err_code)

def example2():
    print('')
    msg = "Describe the picture"
    print(">>", msg)
    resp = qwen3_vl.send(msg)
    err.check_raise(resp.err_code)

example1()
example2()

del qwen3_vl        # Must release vlm object
```

结果：
```
>> 请描述图中有什么
好的，这是一张在城市街道上拍摄的照片。以下是图中包含的详细信息：

这张照片的主体是一位站在红车前的女性，背景是城市街道和建筑。

-   **前景中的女性**：一位女性，她站在画面的前景中央。她有深色的头发，穿着一件深色的外套。她正看着镜头，似乎正准备拍照。

-   **背景中的红车**：在女性的后方，是一辆红色的“大众”（Volkswagen）汽车的前部。这辆车停在一条小巷或路边，它的前脸部分被遮挡，但可以清楚地看到它红色的车身和前大灯。

-   **背景中的建筑物**：在车辆后方是几座多层的建筑，看起来是城市中的居民楼或办公楼。这些建筑的外立面是浅色的，带有许多窗户，窗户的大小和排列方式不同。

-   **照片中的细节**：在图像的右上角，可以看到一辆黑色的汽车的后视镜，这可能是一辆停在远处的车辆。在图像的左上角，有一座建筑的窗户上有一个明显的“N”字母，这可能是一个窗户的标识或装饰。

-   **拍摄视角和构图**：这是一张从较低角度拍摄的风景照。摄影师可能使用了广角镜头，使建筑和街道的细节被放大。整体构图具有一定的对称性，以车辆和建筑为中心。

总的来说，这张照片展示了一个城市街景，其中一位女性在一辆红色的大众汽车前，而背景则是一排具有多个窗户的建筑。

>> Describe the picture
A woman stands on the pavement in front of a red double-decker bus in a city, likely London, given the distinctive bus and the architecture. She is wearing a black jacket and is looking towards the camera. The bus is parked on a street with a white painted line marking the curb. The background consists of buildings with classic architecture.
```

这里从系统加载了一张图片，并且让它描述图中有什么，注意这个模型是**不支持上下文**的，也就是说每次调用`send`函数都是全新的对话，不会记住之前`send`的内容。

另外，默认模型支持`448 x 448`的图片输入分辨率，所以调用`set_image`时，如果分辨率不是这个分辨率，会自动调用`img.resize`方法进行缩放，缩放方法为`fit`指定的方法，比如`image.Fit.FIT_CONTAIN`就是当输入图片分辨率和期望的分辨率比例不一致时采用保持原比例缩放，周围空白填充黑色。
`set_system_prompt` 是系统提示语句，可以适当进行修改来提高你的应用场景的准确率。

注意对于模型`Qwen3-VL-2B-Instruct-GPTQ-Int4-AX630C-P320-CTX448`, `P320`代表`system prompt`和`user prompt`最多只能填充320个token, CTX448代表`system prompt`和`user prompt`以及模型回复的总和最大长度为448个token

### 通过HTTP 接口调用模型
```python
from maix import app, nn, err, image, display, time
import requests
import json

model = "/root/models/Qwen3-VL-2B-Instruct-GPTQ-Int4-AX630C-P320-CTX448-maixcam2/model.mud"
disp = display.Display()

qwen3_vl = nn.Qwen3VL(model)

in_w = qwen3_vl.input_width()
in_h = qwen3_vl.input_height()
in_fmt = qwen3_vl.input_format()
print(f"input size: {in_w}x{in_h}, format: {image.format_name(in_fmt)}")

def on_reply(obj, resp):
    print(resp.msg_new, end="")

qwen3_vl.set_system_prompt("You are Qwen3VL. You are a helpful vision-to-text assistant.")
qwen3_vl.set_reply_callback(on_reply)

# load and set image
img = image.load("/maixapp/share/picture/2024.1.1/ssd_car.jpg", format=in_fmt)
qwen3_vl.set_image(img, fit=image.Fit.FIT_CONTAIN) # if size not math, will auto resize first
disp.show(img)

while not app.need_exit():
    print('wait model is ready')
    if qwen3_vl.is_ready():
        break
    time.sleep(1)

def example3():
    print('')
    url = "http://127.0.0.1:12346"
    headers = {
        "Content-Type": "application/json",
    }

    stream = True
    data = {
        "model": "AXERA-TECH/Qwen3-VL-2B-Instruct-GPTQ-Int4",
        "stream":stream,
        "temperature":0.7,
        "repetition_penalty":1,
        "top-p":0.8,
        "top-k":20,
        "messages": [{
                "role":"user",
                "content": [{
                        "type":"text",
                        "text":"告诉我你的名字"
                    }, {
                        "type":"image_url",
                        "image_url":"images/demo.jpg"
                    }]
                }]
    }
    response = requests.post(url + '/v1/chat/completions', headers=headers, json=data, stream=stream)

    if not stream:
        print(response.status_code)  # 状态码
        print(response.text)         # 响应内容
    else:
        # 处理流式响应
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data_str = line[6:]  # 移除 "data: " 前缀
                        if data_str.strip() == '[DONE]':
                            print("\n流式传输完成")
                            break
                        try:
                            chunk = json.loads(data_str)
                            # 提取模型输出内容
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    print(delta['content'], end='', flush=True)
                        except json.JSONDecodeError:
                            continue
        else:
            print(f"请求失败: {response.status_code}")
            print(response.text)

example3()

del qwen3_vl        # Must release vlm object
```

结果:
```
我是一个人工智能助手，没有名字。我是一个能帮助你解答问题、提供信息和进行有益讨论的虚拟助手。
流式传输完成
```
Qwen3-VL支持openai风格的接口, 可以通过http协议的流式获取模型输入结果.

## 自定义量化模型

上面提供的模型是为 MaixCAM2 量化后的模型，如果需要自己量化模型，可以参考：
* [pulsar2文档](https://pulsar2-docs.readthedocs.io/zh-cn/latest/appendix/build_llm.html)
* 原始模型： https://huggingface.co/Qwen/Qwen3-VL-2B-Instruct
