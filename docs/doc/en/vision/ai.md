---
title: AI vision knowledge
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

MaixPy provides runtime APIs for common vision models. For a first test, you do not need to train a model. Select your board in the [MaixHub model zoo](https://maixhub.com/model/zoo) and download a ready-made model.

If no ready-made model recognizes your target, use [MaixHub online training](./maixhub_train.md) or train on a computer. See [Get, Upload and Run a Model](../ai_model_converter/ai_model_deploy.md) for the complete route.

After preparing the model, upload the complete model package to the device and load it with the matching MaixPy API. The classification, detection, and recognition guides that follow provide working code.
