---
title: MaixPy MaixCAM 运行 Qwen 大语言模型
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


## Qwen 大语言模型简介

近年来大语言模型（LLM）非常火，给工作生活带来了很大的便利，使用LLM，我们可以跟其对话，从聊天到专业指导都能胜任。

Qwen（通义千问）是阿里巴巴集团旗下阿里云研发的开源大语言模型（LLM）和多模态模型（LMM）系列，旨在推动通用人工智能（AGI）的发展。自2023年首次发布以来，Qwen 仍然在保持迭代，并在多个自然语言处理和多模态任务中展现出卓越性能。

更多详细介绍可以自行搜索或到[Qwen官网](https://qwen.readthedocs.io/zh-cn/latest/)查看。

Qwen 实际上包含了许多种模型，本文主要介绍 大语言模型（LLM） Qwen 的使用。

## 基础概念

* Token： 用户输入文字后不是直接将文字输入给模型，而是将文字使用特定的方式进行编码，编码成一个单词表的下标列表。比如通过数据集生成单词表为：
```txt
...
1568 hello
...
1876 world
...
1987 !
1988  (空格)
```
前面的数字是行数，那么我们输入`hello world !`就会被编码为列表 `[1568, 1988, 1876, 1988, 1987]` 这就叫 `token`，这种做法可以大大减少输入字符数量，当然这里只是简单介绍基本原理，实际还会加额外的标识符token等，不同模型 token 词典、算法可能会有区别。
同样，模型输出也是输出 token，最后程序根据字典转为人们认识的字符。

* 上下文：也就是对话上下文，用户和模型对话，用户一句模型一句，语句之间是有记忆和关联的。
* 72B/32B/1.5B/0.5B： 反应了模型的可训练参数规模，B表示 Billion(十亿)，参数越大效果越好但是占用内存越大运行速度越慢。


## MaixPy MaixCAM 中使用 Qwen

### 模型和下载地址

默认系统`/root/models`目录下已经有`1.5B`的模型了，如果没有，可以自行下载。

* **1.5B**:
  * 内存需求：CMM 内存 1.8GiB，内存解释请看[内存使用文档](../pro/memory.md)
  * 下载地址：https://huggingface.co/sipeed/Qwen2.5-1.5B-Instruct-maixcam2
* **0.5B**:
  * 内存需求： CMM 内存 800MiB，内存解释请看[内存使用文档](../pro/memory.md)
  * 下载地址： https://huggingface.co/sipeed/Qwen2.5-0.5B-Instruct-maixcam2

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
huggingface-cli download sipeed/Qwen2.5-1.5B-Instruct-maixcam2 --local-dir Qwen2.5-1.5B-Instruct-maixcam2
```

### 运行模型

```python
from maix import nn, err, log, sys

model = "/root/models/Qwen2.5-1.5B-Instruct/model.mud"
# model = "/root/models/Qwen2.5-0.5B-Instruct/model.mud"
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

### 上下文

因为资源有限，上下文长度也是有限的，比如默认提供的模型大约 512 个 token，而且必须只少有128个空闲 token才能继续对话，比如当历史记录token 500 个（小于 512 但是不够 128 个）就不能继续对话了。
当上下文满了后，目前只能调用`clear_context()`清除对话进行新的对话了。

当然，这个上下文长度也可以改，不过需要重新量化模型，以及太长的上下文会导致模型运行速度下降，有需求可以按照下文自行转换模型。

## 自定义量化模型

上面提供的模型是为 MaixCAM2 量化后的模型，如果需要自己量化模型，可以参考：
* [pulsar2文档](https://pulsar2-docs.readthedocs.io/zh-cn/latest/appendix/build_llm.html)： 进行量化编译。**注意** pulsar2 版本必须 `>= 4.0`。
* 原始模型: https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct
* 更多文章: https://zhuanlan.zhihu.com/p/706645301

默认模型转换命令:
```shell
pulsar2 llm_build --input_path Qwen2.5-0.5B-Instruct  --output_path models/Qwen2.5-0.5B-Instruct-ax630c --hidden_state_type bf16 --prefill_len 128 --kv_cache_len 1023 --last_kv_cache_len 256 --last_kv_cache_len 512 --chip AX620E -c 1
```

可以根据你的需求修改。

