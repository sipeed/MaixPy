---
title: MaixCAM MaixPy Basic Knowledge of AI Vision
update:
  - date: 2024-04-03
    author: neucrack
    version: 1.0.0
    content: Initial documentation
---

## Introduction

If you don't have an AI background, you can first read [What is Artificial Intelligence (AI) and Machine Learning](https://wiki.sipeed.com/ai/en/basic/what_is_ai.html) to understand the basic concepts of AI before learning about AI.

Then, the visual AI we use is generally based on the `deep neural network learning` method. If you are interested, you can check out [Deep Neural Network (DNN) Basics](https://wiki.sipeed.com/ai/en/basic/dnn_basic.html).

## Using Visual AI in MaixPy

Using visual AI in MaixPy is very simple. By default, commonly used AI models are provided, and you can use them directly without having to train the models yourself. You can find the `maixcam` models in the [MaixHub Model Library](https://maixhub.com/model/zoo).

Additionally, the underlying APIs have been well-encapsulated, and you only need to make simple calls to implement them.

If you want to train your own model, you can start with [MaixHub Online Training](https://maixhub.com/model/training/project). On the online platform, you can train models just by clicking, without the need to purchase expensive machines, set up complex development environments, or write code, making it very suitable for beginners and also for experienced users who are too lazy to read code.

Generally, once you have obtained the model file, you can transfer it to the device and call the MaixPy API to use it. The specific calling methods are discussed in the following sections.
