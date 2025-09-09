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

默认系统`/root/models`目录下已经有`0.5B`的模型了，如果没有，可以自行下载。

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

def show_mem_info():
    print("memory info:")
    for k, v in sys.memory_info().items():
        print(f"\t{k:12}: {sys.bytes_to_human(v)}")
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

结果：
```
>> 你好，请介绍你自己
你好！我是Qwen，我是一个由阿里云开发的预训练语言模型。我的设计目的是尽可能多地模拟人类语言的复杂性和多样性。虽然我没有个人记忆或情感，但我可以生成连贯和有意义的文本。如果你有任何问题或需要帮助，请告诉我！

>> 请计算 1990 + 35的值，并给出计算过程
计算的过程如下：

1. 首先，将两个数相加，即 1990 + 35。

2. 将 1990 和 35 对齐数字位数，如下：

   1 9 9 0
 +   3 5
-------
   2 0 2 5

3. 按照从右向左加起来：

   0 + 5 = 5
   2 + 9 = 11（进一，写 2 进 10）
   1 + 9 = 10（进一，写 0 进 10）
   1 + 1 = 2

所以，1990 + 35 的结果是 2025。

>> please calculate 1990 + 35
1990 + 35 = 2025

```

### 上下文

因为资源有限，上下文长度也是有限的，比如默认提供的模型大约 512 个 token，而且必须只少有128个空闲 token才能继续对话，比如当历史记录token 500 个（小于 512 但是不够 128 个）就不能继续对话了。
当上下文满了后，目前只能调用`clear_context()`清除对话进行新的对话了。

当然，这个上下文长度也可以改，不过需要重新量化模型，以及太长的上下文会导致模型运行速度下降，有需求可以按照下文自行转换模型。

## 修改参数

Qwen 模型有一些参数可以修改，会改变模型的一些行为，默认在`model.mud`模型文件中设置了默认值，
当然，你也可以在代码中设置，比如通过`qwen.post_config.temperature = 0.9` 设置即可。
比如参数有：
```ini
[post_config]
enable_temperature = true
temperature = 0.9

enable_repetition_penalty = false
repetition_penalty = 1.2
penalty_window = 20

enable_top_p_sampling = false
top_p = 0.8

enable_top_k_sampling = true
top_k = 10
```

这些参数是用于**控制Qwen模型（或其他大语言模型）生成文本行为**的采样策略设置。它们会影响模型输出的**多样性、随机性和重复程度**。下面逐项解释这些参数的含义：

* `enable_temperature = true`
* `temperature = 0.9`
  * **含义**：启用“温度采样”策略，并将温度值设置为 0.9。
  * **解释**：
    * 温度控制**随机性**。值越低（如 0.1），输出越确定（趋近于贪婪搜索）；值越高（如 1.5），输出越随机。
    * 一般推荐值在 `0.7 ~ 1.0` 之间。
    * 0.9 表示：适当增加输出多样性，但不至于太乱。
* `enable_repetition_penalty = false`
* `repetition_penalty = 1.2`
* `penalty_window = 20`
  * **含义**：
    * 未启用重复惩罚，即使设置了 `repetition_penalty = 1.2`，也不会生效。
    * 如果启用，该机制会降低模型重复使用最近 `20` 个 token 的概率。
  * **解释**：
    * 避免模型“啰嗦”或陷入“重复循环”（如“你好你好你好……”）。
    * 惩罚系数 > 1 表示抑制重复。常见推荐值为 `1.1 ~ 1.3`。
* `enable_top_p_sampling = false`
* `top_p = 0.8`
  * **含义**：
    * 未启用 Top-p（nucleus）采样。
    * 如果启用，模型会从**累计概率前 p 的 token 中采样**，而非全部。
  * **解释**：
    * `top_p = 0.8` 表示：从概率累加值刚好达到 0.8 的那些 token 中进行采样。
    * 比 Top-k 更灵活，可以根据每次生成时 token 分布动态调整候选集。
* `enable_top_k_sampling = true`
* `top_k = 10`
  * **含义**：启用 Top-k 采样，模型每次只从**概率最高的前 10 个 token 中**选择一个输出。
  * **解释**：
    * 是一种限制采样空间的方法，控制输出的多样性。
    * `top_k = 1` 近似于贪婪搜索（最确定）；`top_k = 10` 代表允许一定程度的多样性。


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

