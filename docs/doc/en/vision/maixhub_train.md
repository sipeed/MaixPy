---
title: Using MaixHub to Train AI Models for MaixCAM MaixPy
update:
  - date: 2024-04-03
    author: neucrack
    version: 1.0.0
    content: Initial document
---

## Introduction

MaixHub offers the functionality to train AI models online, directly within a browser. This eliminates the need for expensive hardware, complex development environments, or coding skills, making it highly suitable for beginners as well as experts who prefer not to delve into code.

## Basic Steps to Train a Model Using MaixHub

### Identify the Data and Model Types

To train an AI model, you first need to determine the type of data and model. As of April 2024, MaixHub provides models for image data including `Object Classification Models` and `Object Detection Models`. Object classification models are simpler than object detection models, as the latter require marking the position of objects within images, which can be more cumbersome. Object classification merely requires identifying what is in the image without needing coordinates, making it simpler and recommended for beginners.

### Collect Data

As discussed in AI basics, training a model requires a dataset for the AI to learn from. For image training, you need to create a dataset and upload images to it.

Ensure the device is connected to the internet (WiFi).
Open the MaixHub app on your device and choose to collect data to take photos and upload them directly to MaixHub. You need to create a dataset on MaixHub first, then click on device upload data, which will display a QR code. Scan this QR code with your device to connect to MaixHub.

It's important to distinguish between training and validation datasets. To ensure the performance during actual operation matches the training results, the validation dataset must be of the same image quality as those taken during actual operation. It's also advisable to use images taken by the device for the training set. If using internet images, restrict them to the training set only, as the closer the dataset is to actual operational conditions, the better.

### Annotate Data

For classification models, images are annotated during upload by selecting the appropriate category for each image.

For object detection models, after uploading, you need to manually annotate each image by marking the coordinates, size, and category of the objects to be recognized.
This annotation process can also be done offline on your own computer using software like labelimg, then imported into MaixHub using the dataset import feature.
Utilize shortcuts during annotation to speed up the process. MaixHub will also add more annotation aids and automatic annotation tools in the future (there is already an automatic annotation tool available for videos that you can try).

### Train the Model

Select training parameters, choose the corresponding device platform, select maixcam, and wait in the training queue. You can monitor the training progress in real-time and wait for it to complete.

### Deploy the Model

Once training is complete, you can use the deploy function in the MaixHub app on your device to scan a code and deploy.
The device will automatically download and run the model, storing it locally for future use.

If you find the recognition results satisfactory, you can share the model to the model library with a single click for others to use.

## How to Use

Please visit [MaixHub](https://maixhub.com) to register an account, then log in. There are video tutorials on the homepage for learning.

Note that if the tutorial uses the M2dock development board, the process is similar for MaixCAM, although the MaixHub application on the device might differ slightly. The overall process is the same, so please apply the knowledge flexibly.
