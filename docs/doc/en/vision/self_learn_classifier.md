---
title: MaixPy Self-Learning Classifier
---

## Introduction to MaixPy Self-Learning Classifier

Typically, to recognize new categories, it is necessary to collect a new dataset and train on a computer, which can be cumbersome and complex. This method eliminates the need for computer-based training, allowing for immediate learning of new objects directly on the device, suitable for less complex scenarios.

For example, if there are a drink bottle and a mobile phone in front of you, take a photo of each to serve as the basis for two categories. Then, collect several photos from different angles of each item, extract their features and save them. During recognition, the image's features are compared with the saved feature values, and the closest match determines the classification.

## Using the Self-Learning Classifier in MaixPy

Steps:

* Collect n classification images.
* Collect n*m images, m images for each category, order does not matter.
* Start learning.
* Recognize images and output results.

Simplified version of the code, for the full version please refer to the complete code in the example.

```python
from maix import nn, image

classifier = nn.SelfLearnClassifier(model="/root/models/mobilenetv2.mud", feature_layer=None)

img1 = image.load("/root/1.jpg")
img2 = image.load("/root/2.jpg")
img3 = image.load("/root/3.jpg")
sample_1 = image.load("/root/sample_1.jpg")
sample_2 = image.load("/root/sample_2.jpg")
sample_3 = image.load("/root/sample_3.jpg")
sample_4 = image.load("/root/sample_4.jpg")
sample_5 = image.load("/root/sample_5.jpg")
sample_6 = image.load("/root/sample_6.jpg")


classifier.add_class(img1)
classifier.add_class(img2)
classifier.add_class(img3)
classifier.add_sample(sample_1)
classifier.add_sample(sample_2)
classifier.add_sample(sample_3)
classifier.add_sample(sample_4)
classifier.add_sample(sample_5)
classifier.add_sample(sample_6)

classifier.learn()

img = image.load("/root/test.jpg")
max_idx, max_score = classifier.classify(img)
print(max_idx, max_score)
```
