---
title: Running the DeepSeek R1 Large Language Model on MaixPy MaixCAM
update:
  - date: 2025-05-28
    author: neucrack
    version: 1.0.0
    content: Added DeepSeek code and documentation
---

## Supported Devices

| Device   | Supported |
| -------- | --------- |
| MaixCAM2 | ✅         |
| MaixCAM  | ❌         |

## Introduction to the DeepSeek Large Language Model

In recent years, large language models (LLMs) have become extremely popular, bringing great convenience to both work and daily life. With LLMs, we can interact with them in natural conversation, ranging from casual chat to professional guidance.

DeepSeek-R1 is a large language model (LLM) developed by DeepSeek-AI. It features reasoning capabilities and functions similarly to Qwen.

Like other models, it comes in various parameter sizes, such as 72B, 32B, 7B, and 1.5B. Due to memory and computational limitations, MaixCAM2 can only run the 1.5B version.

The 1.5B version is essentially a distilled version based on Qwen2.5. That means it is fundamentally a Qwen2.5 model, with differences in datasets and training methods. Therefore, the usage is basically the same as Qwen, and we won’t repeat the instructions here.

## Running DeepSeek R1 on MaixPy MaixCAM

As mentioned above, since the network structure is the same as Qwen2.5, please refer to the [Qwen Documentation](./llm_qwen.md). Below is a usage example:

### Running the Model

Model download link: [https://huggingface.co/sipeed/deepseek-r1-distill-qwen-1.5B-maixcam2](https://huggingface.co/sipeed/deepseek-r1-distill-qwen-1.5B-maixcam2)
Memory requirement: 2GiB

```python
from maix import nn, err, log, sys

model = "/root/models/deepseek-r1-distill-qwen-1.5B/model.mud"
log.set_log_level(log.LogLevel.LEVEL_ERROR, color = False)

def bytes_to_human(b):
    """Convert bytes to a human-readable format."""
    if b < 1024:
        return f"{b} B"
    elif b < 1024**2:
        return f"{b / 1024:.2f} KB"
    elif b < 1024**3:
        return f"{b / 1024**2:.2f} MB"
    else:
        return f"{b / 1024**3:.2f} GB"

def show_mem_info():
    print("memory info:")
    for k, v in sys.memory_info().items():
        print(f"\t{k:12}: {bytes_to_human(v)}")
    print("")

show_mem_info()
qwen = nn.Qwen(model)
show_mem_info()

def on_reply(obj, resp):
    print(resp.msg_new, end="")

qwen.set_system_prompt("You are Qwen, created by Alibaba Cloud. You are a helpful assistant.")
qwen.set_reply_callback(on_reply)

msg = "Hello, please introduce yourself."
print(">>", msg)
resp = qwen.send(msg)
err.check_raise(resp.err_code)

msg = "Please calculate 1990 + 35 and provide the calculation steps."
print(">>", msg)
resp = qwen.send(msg)
err.check_raise(resp.err_code)

qwen.clear_context()

msg = "please calculate 1990 + 35"
print(">>", msg)
resp = qwen.send(msg)
err.check_raise(resp.err_code)
# print(resp.msg)
```

