---
title: MaixPy MaixCAM 运行 DeepSeek R1 大语言模型
update:
  - date: 2025-05-28
    author: neucrack
    version: 1.0.0
    content: 新增 Qwen 代码和文档
---

## 支持的设备

| 设备      | 是否支持 |
| -------- | ------- |
| MaixCAM2 | ✅ |
| MaixCAM  | ❌ |


## DeepSeek 大语言模型简介

近年来大语言模型（LLM）非常火，给工作生活带来了很大的便利，使用LLM，我们可以跟其对话，从聊天到专业指导都能胜任。

DeepSeek-R1 是深势科技（DeepSeek-AI）研发的大语言模型（LLM），具备思考功能，功能和 Qwen 类似。

同样也根据参数量分为很多版本，比如 72B 32B 7B 1.5B 等，对于 MaixCAM2 由于内存和算力限制只能跑到 1.5B。

而 1.5B 版本事实上也是基于 Qwen2.5 进行蒸馏，也就是说本质上还是一个 Qwen2.5 模型，只是数据集和训练方法不同，因此，使用方法和 Qwen 的使用方法基本一致，本文就不再复述一遍了。

## 在 MaixPy MaixCAM 运行 DeepSeek R1

如上所述，网络结构和 Qwen2.5 一致，所以请看 [Qwen 文档](./llm_qwen.md)，下面是示例：

### 运行模型

模型下载地址： https://huggingface.co/sipeed/deepseek-r1-distill-qwen-1.5B-maixcam2
内存需求： 2GiB

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

msg = "你好，请介绍你自己"
print(">>", msg)
resp = qwen.send(msg)
err.check_raise(resp.err_code)

msg = "请计算 1990 + 35的值，并给出计算过程"
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

