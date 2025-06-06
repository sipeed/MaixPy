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

As mentioned above, since the network structure is the same as Qwen2.5, please refer to the [Qwen Documentation](./llm_qwen.md).

### Models and Download Links

By default, if `/root/models` directory in the system have no model, you can download it manually.

* **1.5B**:

  * Memory requirement: CMM memory 1.8GiB. See [Memory Usage Documentation](../pro/memory.md) for explanation.
  * Download link: https://huggingface.co/sipeed/deepseek-r1-distill-qwen-1.5B-maixcam2

Download method please refer to [Qwen Documentation](./llm_qwen.md).

### Running the Model

Model download link: [https://huggingface.co/sipeed/deepseek-r1-distill-qwen-1.5B-maixcam2](https://huggingface.co/sipeed/deepseek-r1-distill-qwen-1.5B-maixcam2)
Memory requirement: 2GiB

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

Result:
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


## Modifying Parameters

Refer to [Qwen Documentation](./llm_qwen.md)。

