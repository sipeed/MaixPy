---
title: AI Model Download, Debugging, and Deployment Guide
---

## Choose a Model Deployment Workflow

Before deploying a local model on MaixCAM / MaixCAM-Pro / MaixCAM2, first identify the model source, target device, and deployment path. Choose the workflow that matches your current resources: do not retrain a model if a ready-made one already works; train first when you need custom classes; after obtaining a `.pt` file, export it to ONNX and prefer the online conversion platform to generate deployable model files. Manual command-line conversion is an advanced workflow for custom conversion parameters or deeper debugging.

| Goal | Recommended workflow | Documentation |
| --- | --- | --- |
| Use built-in or ready-made models | Use built-in models first. For more resolutions or class sets, choose the matching device platform in [MaixHub Model Zoo](https://maixhub.com/model/zoo). MaixCAM / MaixCAM-Pro model packages usually include `.mud` and `.cvimodel` files, while MaixCAM2 model packages usually include `.mud` and `.axmodel` files. Place the files from the same package in the same directory on the device | [Model and dataset sources](../pro/datasets.md) |
| Train a custom recognition target | Use MaixHub online training to complete data collection, annotation, training, and deployment | [MaixHub online training](../vision/maixhub_train.md) |
| Train a YOLO model offline | Prepare the dataset and train the YOLO model on a computer. Use the recommended Ultralytics versions for training and export. After training produces a `.pt` file, export it to an ONNX model with a fixed input size | [YOLO model offline training](../vision/customize_model_yolo.md) |
| Convert a YOLO model online | Upload the ONNX model and a ZIP archive containing 20-100 calibration images. The platform generates `.mud` + `.cvimodel` for MaixCAM / MaixCAM-Pro, or `.mud` + `.axmodel` for MaixCAM2 | [Online graphical model conversion platform](./online_converter.md) |
| Convert an ONNX model manually | Use command-line conversion when you need custom output nodes, conversion parameters, toolchain configuration, or when online conversion does not meet the requirement | [MaixCAM2 model conversion](./maixcam2.md) / [MaixCAM model conversion](./maixcam.md) / [Trim ONNX model output nodes](./onnx_export.md) |
| Self-host the conversion platform | Use this when uploading models to the online service is not suitable, or when you need intranet deployment, a self-managed conversion server, or platform-source debugging | [Self-hosted graphical model conversion platform](./web_converter.md) |
| Port a new AI model | Use this for model types not yet wrapped by MaixPy, where you need to handle preprocessing, postprocessing, MUD description, and inference code yourself | [Port a new AI model](../pro/customize_model.md) |

After choosing your workflow, continue with the corresponding document.
