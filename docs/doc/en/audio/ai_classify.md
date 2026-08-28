---
title: AI audio classification
---


This page does not yet provide a complete sound-classification training and deployment guide. Two advanced routes are currently available:

- Use a classification model with audio input and follow [Port an Unsupported Model](../pro/customize_model.md) to add preprocessing and inference code.
- Convert audio into spectrogram images, then train an image classifier. A spectrogram shows how the strength of each frequency changes over time.

Both routes require your own training and data-processing code. If you only need to recognize a fixed command, start with [Keyword Recognition](./keyword.md).
