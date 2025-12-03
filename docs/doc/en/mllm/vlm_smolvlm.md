---
title: MaixPy MaixCAM Running SmolVLM Visual Language Model
update:
  - date: 2025-12-03
    author: lxowalle
    version: 1.0.0
    content: Added SmolVLM code and documentation
---

## Supported Devices

| Device   | Supported |
| -------- | --------- |
| MaixCAM2 | ✅         |
| MaixCAM  | ❌         |

## Introduction to SmolVLM

VLM (Vision-Language Model) refers to models that can take text + image input and output text, such as describing the content in an image—essentially enabling the AI to “see.”
SmolVLM currently supports English only.

## Using SmolVLM in MaixPy MaixCAM

### Model and Download Address

If the `SmolVLM` model is not present in the default `/root/models` directory, you need to download it manually.
 * Memory requirement: CMM memory 300MB. For more information, see [the memory usage documentation](../pro/memory.md)

 * Download link: https://huggingface.co/sipeed/smolvlm-256m-instruct-maixcam2

The download method is the same as described in [the Qwen documentation](./llm_qwen.md)

### Running the Model

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

Output:
```
>> Describe the picture
The image depicts a prominent bus stop, specifically in the middle, where a young woman is captured and standing on the sidewalk. The bus, which appears to be a double-decker bus, is prominently displayed in the center of the image. The bus is red with bold white text and design elements on its side. The text on the bus reads "THING'S GET MORE EXCITING."

Below this text is a small image of the bus logo. The bus is parked next to another bus, both in a city background. The background on which the bus is parked is not clearly discernible due to the perspective, but it looks urban due to the buildings and street signs visible.

The woman in the image is looking towards the bus on the street, possibly waiting to board or simply admiring the scene. She is wearing a black coat, and her hair is short and dark. The bus itself has a red roof, and its windows are visible. The bus’s front is also visible, but it is not as prominent as the bus’s front side.

In the background, there are buildings and a large glass window. The sky is not visible, but it is bright, as indicated by the light reflection on the windows. The street is wide and seems to be a busy urban street, possibly with cars and other vehicles.

The bus stop itself seems to be in an area that is busy. There are traffic signs visible, and the sidewalk looks well-maintained. The street is wide enough for a bus to pass by at a distance, though it is not very wide. The overall environment appears modern and functional.

This vivid depiction of the bus stop and the surrounding environment provides a clear and detailed view of the scene.
```

Additionally, the default model supports an image input resolution of `512×512`, so when calling `set_image`, if the image resolution does not match, it will automatically call `img.resize` to scale it. The scaling method is controlled by the `fit` parameter. For example, `image.Fit.FIT_CONTAIN` preserves the original aspect ratio and fills the padding with black when the aspect ratio differs from the required resolution.

## Custom Quantized Model
Some model parameters can be modified. Refer to [the Qwen documentation](./llm_qwen.md) for details.

## Custom Quantized Model

The model provided above is a quantized model for MaixCAM2. If you want to quantize your own model, refer to:

* [Pulsar2 Documentation](https://pulsar2-docs.readthedocs.io/zh-cn/latest/appendix/build_llm.html)
* Original model: https://huggingface.co/HuggingFaceTB/SmolVLM-256M-Instruct
