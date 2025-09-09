---
title: Running Qwen LLM on MaixPy MaixCAM
update:
  - date: 2025-05-28
    author: neucrack
    version: 1.0.0
    content: Added Qwen code and documentation
---

## Supported Devices

| Device    | Supported |
| --------- | --------- |
| MaixCAM2  | ✅         |
| MaixCAM   | ❌         |


## Introduction to Qwen LLM

In recent years, large language models (LLMs) have gained significant popularity, bringing great convenience to work and daily life. With LLMs, we can interact via dialogue, handling everything from casual chatting to professional guidance.

Qwen (Tongyi Qianwen) is a series of open-source large language models (LLMs) and multimodal models (LMMs) developed by Alibaba Cloud under Alibaba Group. It aims to advance the development of Artificial General Intelligence (AGI). Since its first release in 2023, Qwen has continued to evolve and has demonstrated outstanding performance in various natural language processing and multimodal tasks.

For more detailed information, feel free to search or visit the [Qwen official site](https://qwen.readthedocs.io/zh-cn/latest/).

Qwen actually includes many different models. This document mainly introduces the usage of the large language model (LLM) Qwen.

## Basic Concepts

* Token: After a user inputs text, the text is not directly passed to the model. Instead, it is encoded in a specific way into a list of vocabulary indexes. For example, a vocabulary generated from a dataset might be:
```txt
...
1568 hello
...
1876 world
...
1987 !
1988  (space)
````

The preceding numbers are line numbers, so if we input `hello world !`, it will be encoded as the list `[1568, 1988, 1876, 1988, 1987]`. This is called a `token`. This approach significantly reduces the number of input characters. Of course, this is just a basic introduction; in practice, extra identifier tokens, etc., are also included, and different models may have different token vocabularies and algorithms. Similarly, model outputs are also in tokens, which the program then converts back into human-readable text.

* Context: This refers to the dialogue context — interactions between the user and the model. The utterances are remembered and related to each other.
* 72B/32B/1.5B/0.5B: These indicate the scale of trainable parameters in the model, with B representing Billion (one billion). The larger the parameters, the better the performance, but they require more memory and run slower.

## Using Qwen on MaixPy MaixCAM

### Models and Download Links

By default, the `/root/models` directory in the system already contains the `0.5B` model. If not, you can download it manually.

* **1.5B**:

  * Memory requirement: CMM memory 1.8GiB. See [Memory Usage Documentation](../pro/memory.md) for explanation.
  * Download link: [https://huggingface.co/sipeed/Qwen2.5-1.5B-Instruct-maixcam2](https://huggingface.co/sipeed/Qwen2.5-1.5B-Instruct-maixcam2)
* **0.5B**:

  * Memory requirement: CMM memory 800MiB. See [Memory Usage Documentation](../pro/memory.md) for explanation.
  * Download link: [https://huggingface.co/sipeed/Qwen2.5-0.5B-Instruct-maixcam2](https://huggingface.co/sipeed/Qwen2.5-0.5B-Instruct-maixcam2)

### Download Method

First, make sure the download tool is installed:

```
pip install huggingface_hub
```

In mainland China, you can use:

```
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple huggingface_hub
```

If you're in mainland China, you can set a domestic mirror for faster download speed:
Linux/MacOS:

```
export HF_ENDPOINT=https://hf-mirror.com
```

Windows:
CMD terminal: `set HF_ENDPOINT=https://hf-mirror.com`
PowerShell: `$env:HF_ENDPOINT = "https://hf-mirror.com"`

Then download:

```shell
huggingface-cli download sipeed/Qwen2.5-1.5B-Instruct-maixcam2 --local-dir Qwen2.5-1.5B-Instruct-maixcam2
```

### Running the Model

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

Result:
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

### Context

Due to limited resources, the context length is also limited. For example, the default model supports about 512 tokens, and at least 128 free tokens must remain to continue the dialogue. For instance, if the historical tokens reach 500 (which is less than 512 but not enough free tokens), further dialogue is not possible.

When the context is full, you currently must call `clear_context()` to clear the dialogue and start a new one.

Of course, this context length can be modified, but doing so requires re-quantizing the model. Also, longer context length can slow down model performance. If needed, you can convert the model yourself as described below.

## Modifying Parameters

The Qwen model allows certain parameters to be modified, which can change the model's behavior. Default values are typically set within the `model.mud` file, 
Of course, you can also set these values programmatically, for example:

```python
qwen.post_config.temperature = 0.9
```

configs for example:

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

These parameters are used to **control the text generation behavior** of the Qwen model (or other large language models) through sampling strategies. They affect the **diversity, randomness, and repetition** of the output. Below is an explanation of each parameter:

* `enable_temperature = true`
* `temperature = 0.9`
  * **Meaning**: Enables the "temperature sampling" strategy and sets the temperature value to 0.9.
  * **Explanation**:
    * Temperature controls **randomness**. Lower values (e.g., 0.1) result in more deterministic outputs (similar to greedy search), while higher values (e.g., 1.5) increase randomness.
    * A recommended range is typically between `0.7 ~ 1.0`.
    * A value of 0.9 means a moderate increase in diversity without making the output too chaotic.
* `enable_repetition_penalty = false`
* `repetition_penalty = 1.2`
* `penalty_window = 20`
  * **Meaning**:
    * Repetition penalty is disabled, so the value `repetition_penalty = 1.2` has no effect.
    * If enabled, this mechanism reduces the probability of repeating tokens from the most recent `20` tokens.
  * **Explanation**:
    * Helps prevent the model from being verbose or getting stuck in repetitive loops (e.g., “hello hello hello…”).
    * A penalty factor > 1 suppresses repetition. A common recommended range is `1.1 ~ 1.3`.
* `enable_top_p_sampling = false`
* `top_p = 0.8`
  * **Meaning**:
    * Top-p (nucleus) sampling is disabled.
    * If enabled, the model samples from **the smallest set of tokens whose cumulative probability exceeds p**, instead of from all tokens.
  * **Explanation**:
    * `top_p = 0.8` means sampling from tokens whose cumulative probability just reaches 0.8.
    * More flexible than top-k, as it adapts the candidate set dynamically based on the token distribution in each generation step.
* `enable_top_k_sampling = true`
* `top_k = 10`
  * **Meaning**: Enables top-k sampling, where the model selects output tokens from the **top 10 most probable tokens**.
  * **Explanation**:
    * This is a way to constrain the sampling space and control output diversity.
    * `top_k = 1` approximates greedy search (most deterministic), while `top_k = 10` allows for a moderate level of diversity.

## Custom Quantized Models

The models provided above are quantized specifically for MaixCAM2. If you need to quantize your own models, refer to:
* [pulsar2 documentation](https://pulsar2-docs.readthedocs.io/zh-cn/latest/appendix/build_llm.html): for quantization and compilation. **Note**: pulsar2 version must be `>= 4.0`.
* Original model: https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct
* More article: https://zhuanlan.zhihu.com/p/706645301

Default model conversion command:

```shell
pulsar2 llm_build --input_path Qwen2.5-0.1B-Instruct  --output_path models/Qwen2.5-1.5B-Instruct-ax630c --hidden_state_type bf16 --prefill_len 128 --kv_cache_len 1023 --last_kv_cache_len 256 --last_kv_cache_len 512 --chip AX620E -c 1
```

You can modify it based on your own needs.
