---
title: MaixCAM MaixP Where to Find Datasets for Training Models
---

## What Are Datasets Used For?

Datasets are essential for training machine learning models. They provide the labeled data that models use to learn patterns and features, enabling them to perform specific tasks such as object detection, image classification, or keypoint detection.

## Is It Possible Not to Use a Dataset?

Yes, it is possible!  

Instead of training your own model, you can use open-source pre-trained models. For example, there are many pre-trained models available for YOLO11, YOLOv8, and YOLOv5. One such source is [this repository](https://github.com/Eric-Canas/qrdet/releases), where you can download YOLOv8 models for QR code detection (`qrdet-*.pt`) then can be convert [model for MaixCAM](https://maixhub.com/model/zoo/480). These models can be exported to ONNX format and then converted to a format supported by MaixCAM.

## Where to Find Datasets

### Option 1: Use Official Datasets from Algorithm Providers
For models like YOLO11 or YOLOv8, you can find many open-source datasets in the [YOLO Official Documentation - Datasets](https://docs.ultralytics.com/datasets/). These datasets are ready to use, and training can be done with a single command as per the documentation. After training, you can export the model to ONNX format and convert it to work with MaixCAM.

### Option 2: Use Dataset Platforms
Platforms such as [Kaggle](https://www.kaggle.com/datasets/riondsilva21/hand-keypoint-dataset-26k) and [Roboflow](https://universe.roboflow.com/) provide extensive collections of datasets for various tasks. You can search for and download datasets that fit your needs.

### Option 3: Create Your Own Dataset in YOLO Format
If you have access to open-source datasets, you can reformat them to make them compatible with YOLO and use them for training. This option provides flexibility and allows you to tailor datasets to your specific application.

