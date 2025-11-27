---
title: MaixPy MaixCAM Running VLM Qwen3-VL Visual Language Model
update:
  - date: 2025-11-27
    author: lxowalle
    version: 1.0.0
    content: Added Qwen3-VL code and documentation
---

## Supported Devices

| Device   | Supported |
| -------- | --------- |
| MaixCAM2 | ✅         |
| MaixCAM  | ❌         |


## Introduction to Qwen3-VL

`Qwen3-VL` is a visual language model from the Qwen series. Compared to the previous generation, it offers superior text comprehension and generation, deeper visual perception and reasoning, extended context length, enhanced spatial and video dynamic understanding, and stronger agent interaction capabilities.

[Qwen3-VL-2B](https://huggingface.co/Qwen/Qwen3-VL-2B-Instruct) has been ported to MaixPy.

## Using Qwen3-VL in MaixPy MaixCAM

### Model and Download Address

MaixPy currently supports `Qwen3-VL-2B-Instruct-GPTQ-Int4-AX630C-P320-CTX448`. Due to the large model size, you need to download the model yourself and save it to the `/root/models directory`.
> !!! IMPORTANT !!! IMPORTANT !!! The model MUST be saved in the `/root/models` directory, otherwise the model cannot be loaded. For example, the save path should be `/root/models/sipeed/Qwen3-VL-2B-Instruct-GPTQ-Int4-AX630C-P320-CTX448-maixcam2`

* **2B**:
  * Memory Requirement: 2GiB CMM Memory. Please refer to the Memory Usage Documentation for memory explanation.
  * Download Address: [Qwen3-VL-2B-Instruct-GPTQ-Int4-AX630C-P320-CTX448-maixcam2](https://huggingface.co/sipeed/Qwen3-VL-2B-Instruct-GPTQ-Int4-AX630C-P320-CTX448-maixcam2)

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
huggingface-cli download sipeed/Qwen3-VL-2B-Instruct-GPTQ-Int4-AX630C-P320-CTX448-maixcam2 --local-dir Qwen3-VL-2B-Instruct-GPTQ-Int4-AX630C-P320-CTX448-maixcam2
```


### Running the Model

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

Result:
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

Here, an image is loaded from the system, and the model is asked to describe what is in the picture. Note that this model does not support context, meaning each call to the `send` function is a completely new conversation and does not remember the content from previous `send` calls.

Additionally, the default model supports an input image resolution of `448 x 448`. Therefore, when calling `set_image`, if the resolution does not match, the `img.resize` method will be automatically called for scaling, using the method specified by `fit`. For example, `image.Fit.FIT_CONTAIN` means that when the aspect ratio of the input image does not match the expected resolution, the original aspect ratio is maintained during scaling, and the surrounding area is filled with black.
`set_system_prompt` is the system prompt statement, which can be appropriately modified to improve accuracy in your application scenario.

Note: For the model `Qwen3-VL-2B-Instruct-GPTQ-Int4-AX630C-P320-CTX448`, `P320` means that `the system prompt` and `user prompt` can only be filled with up to `320 tokens` in total. `CTX448` means the maximum total length for `the system prompt`, `user prompt`, and the model's reply combined is `448 tokens`.

### Calling the Model with HTTP
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
                        "text":"What is your name?"
                    }, {
                        "type":"image_url",
                        "image_url":"images/demo.jpg"
                    }]
                }]
    }
    response = requests.post(url + '/v1/chat/completions', headers=headers, json=data, stream=stream)

    if not stream:
        print(response.status_code)
        print(response.text)
    else:
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data_str = line[6:]
                        if data_str.strip() == '[DONE]':
                            print("\nStreaming finished")
                            break
                        try:
                            chunk = json.loads(data_str)
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    print(delta['content'], end='', flush=True)
                        except json.JSONDecodeError:
                            continue
        else:
            print(f"Request failed: {response.status_code}")
            print(response.text)

example3()

del qwen3_vl        # Must release vlm object
```

Result:
```
I am an AI assistant without a name. I am a virtual assistant capable of helping you answer questions, provide information, and engage in beneficial discussions.
Streaming finished
```
Qwen3-VL supports an OpenAI-style interface, allowing you to obtain the model's output results via HTTP protocol streaming.

## Custom Quantized Model

The model provided above is a quantized model for MaixCAM2. If you want to quantize your own model, refer to:

* [Pulsar2 Documentation](https://pulsar2-docs.readthedocs.io/zh-cn/latest/appendix/build_llm.html)
* Original model: https://huggingface.co/Qwen/Qwen3-VL-2B-Instruct
