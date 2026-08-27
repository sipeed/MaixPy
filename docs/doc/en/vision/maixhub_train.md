---
title: Train Online with MaixHub
---

This guide uses an apple detector as an example. You will collect pictures, annotate them, and train on MaixHub without installing training tools on your computer.

Before starting, prepare your board, MaixVision, and a MaixHub account. Connect the board to the internet.

## Create a project

Sign in to [MaixHub](https://maixhub.com), open model training, and create a project.

Choose **image detection** as the project type. A detection model finds each apple and draws a box around it. An image-classification model only decides what the whole picture contains and cannot show the object's position.

Choose your actual target board: MaixCAM, MaixCAM Pro, or MaixCAM2. A result built for the wrong board cannot run directly.

## Add a class and pictures

Create a dataset and add the class `apple`. The final model keeps the class names and their order, so do not change them halfway through the project.

Using the board to collect pictures is recommended:

1. Select the training set on the MaixHub data-collection page and create a QR code.
2. Open the MaixHub app on the board, scan the code, and take pictures to upload.
3. Return to the website, select the validation set, create a new QR code, and take a different group of pictures.

The model learns from the training set. The validation set checks whether it can handle pictures it did not learn from. Never put the same photo in both sets.

Change the apple, position, background, and lighting. Include a few tables with no apple, so the model does not mistake a red cup for one. See [Prepare a Model and Dataset](../pro/datasets.md) for more tips.

## Annotate every apple

Open the annotation page. Mark each apple with a rectangle close to its edge, then select `apple`.

Draw one box for every apple in the picture. Annotate both training and validation sets. A missed apple gives the model a contradictory answer, so check a few random pictures before starting training.

## Start training

Create a training task, choose the dataset and the correct board, and use the recommended settings for the first run.

After training finishes, inspect the validation pictures:

- Was every apple found?
- Are the boxes close to the apples?
- Are there unwanted boxes on the background?
- Does a different kind of apple still work?

If one type of scene often fails, add more pictures of that scene and train again. More training rounds alone may not fix missing data.

## Download and run the model

Open the deployment page for the training result. Follow the QR-code deployment instructions, or choose manual deployment and download the model package.

For manual deployment, unzip the package:

- MaixCAM or MaixCAM Pro: upload the `.mud` and `.cvimodel` files.
- MaixCAM2: upload the `.mud` file and every `.axmodel` file in the package.

Use MaixVision to upload them to `/root/models` on the board. The package usually includes `main.py`. Open it, make sure its model path points to the uploaded `.mud` file, and run it.

Point the camera at an apple. If the screen shows `apple`, a score, and a box, training and deployment worked. If there is no example code, use the [general run example](../ai_model_converter/ai_model_deploy.md#run-the-model).

## Optional: share the model

First test with another apple, background, and lighting. Once it works in real scenes, training and deployment are complete.

If you want other users to download or discuss it, choose **Share to Model Zoo** in the training project. Describe its purpose, suitable distance, and known limits, and add a picture of it running on the board. Credit any public images and their licenses.

## Troubleshooting

- **Training cannot start:** check that both sets contain enough pictures and that all targets are annotated.
- **Works on the website but not on the board:** rebuild the validation set with real pictures from the board and add failed scenes.
- **Model file not found:** confirm that the files are in `/root/models` and check the `.mud` filename in the code.
- **Want control over training commands:** follow [Train a YOLO Detection Model on a Computer](./customize_model_yolo.md), then use online conversion.
