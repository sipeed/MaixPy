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

如上所述，网络结构和 Qwen2.5 一致，所以请先看 [Qwen 文档](./llm_qwen.md)。

### 模型和下载地址

默认系统`/root/models`目录下如果没有模型，可以自行下载。

* **1.5B**:
  * 内存需求：CMM 内存 1.8GiB，内存解释请看[内存使用文档](../pro/memory.md)
  * 下载地址：https://huggingface.co/sipeed/deepseek-r1-distill-qwen-1.5B-maixcam2

下载方法参考[Qwen 文档](./llm_qwen.md) 里面的下载方法。


### 运行模型

模型下载地址： https://huggingface.co/sipeed/deepseek-r1-distill-qwen-1.5B-maixcam2
内存需求： 2GiB

```python
from maix import nn, err, log, sys

model = "/root/models/deepseek-r1-distill-qwen-1.5B/model.mud"
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

结果
```
    >> Hello, please introduce yourself.
    <think>
    Alright, the user sent "Hello, please introduce yourself." and then added a bot message saying, "You are Qwen, created by Alibaba Cloud."

    I should respond warmly in Chinese. I need let them know I'm here to help with any questions they have and also mention how I can assist them further.

    I should phrase it politely, making sure it's clear and friendly. Also, it's good to offer to help them with whatever they're curious about.

    I think that covers it. I'll keep it concise and positive.
    </think>

    你好！我是AI助手，由阿里巴巴AI研究有限公司开发，很高兴能为您提供帮助。有什么我可以帮助你的吗？

    >> Please calculate 1990 + 35 and provide the calculation steps.
    <think>
    好，让我看看用户的查询。用户给了一个计算题：“请计算1990加35，并提供计算步骤。”看起来用户是一位学生，可能刚刚学过数学，需要练习加法。用户希望得到详细的计算步骤。

    首先，我需要确认用户的具体需求。用户明确要求计算步骤，所以我要仔细检查计算是否正确，以及步骤是否清晰。计算1990加35，首先可以从个位开始相加，然后是十位，再是百位和千位，如果有进位的话。

    我得确保每个步骤都准确无误，确保用户理解每一步是怎么进行的。另外，我要注意数字的排列是否正确，避免笔误。如果用户需要，我可以补充其他数学问题，帮助他们进一步学习。

    总之，我的回答应该包括计算过程的详细说明，确保用户能够一步步理解如何进行加法操作，同时也提供一些额外的信息和可能的补充帮助。
    </think>

    好的，让我来计算一下1990加35的步骤吧!

    首先，写下这两个数字：
    ```
    1990
    +  35
    -------
    ```

    **步骤1：对齐数字**
    将两个数字对齐，确保它们的位数对齐。也就是说，个位对齐，十位对齐，百位对齐，千位对齐。

    ```
    1990
    +   35
    -------
    ```

    **步骤2：从个位开始相加**
    个位的数字是0和5，相加的结果是5。写下这个结果，个位是5。

    ```
    1990
    +    35
    -------
        5
    ```

    **步骤3：处理十位**
    十位的数字是9和3相加，再加上前面个位的进位（但这里没有进位）。9加3等于12。写下2，并将1作为进位。

    ```
    1990
    +    35
    -------
        25
    ```

    **步骤4：处理百位**
    百位的数字是9和0相加，再加上前面的进位（1）。9加0等于9，加上进位的1，等于10。写下0，并将1作为进位到千位。

    ```
    1990
    +    35
    -------
    125
    ```

    **步骤5：处理千位**
    千位的数字是1和0，再加上前面的进位（1）。1加0等于1，加上进位的1，等于2。写下2。

    ```
    1990
    +    35
    -------
    2025
    ```

    所以，最终的计算结果是：
    ```
    1990 + 35 = 2025
    ```

    >> please calculate 1990 + 35
    <think>
    Okay, so I need to calculate 1,9990 plus 35. Wait, that doesn't seem right. 1,990 sounds like a number with a comma in it, but I'm not sure. Maybe the comma is a thousands separator? So, 1,990 would be 1,990, right? Hmm, that makes more sense. So, I'm supposed to add 1,990 and 35.

    Let me try that again. 1,900 plus 90 is 1,990. Yeah, okay, that's correct. So, 1,990 plus 35 would be adding 35 to 1,990. So, 1,990 plus 30 is 2,020, and then plus 5 makes 2,025. So, the answer should be 2,025. Wait, but I'm not a math expert, so maybe I should double-check that. 1,990 is the same as 1990, right? Yeah, 1,000 plus 990 is 1,990. Adding 35, so 1,990 plus 35 equals 2,025. Yeah, that makes sense.
    </think>

    The sum of 1,990 and 35 is calculated as follows:

    1,990 + 35 = 2,025.

    **Answer:** 2,025

```

## 修改参数

Qwen 模型有一些参数可以修改，会改变模型的一些行为，参考[Qwen 文档](./llm_qwen.md)。



