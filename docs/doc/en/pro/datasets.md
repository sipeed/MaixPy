---
title: Prepare a Model and Dataset
---

There are two ways to make a board recognize apples: use a model someone already made, or train your own model with your own pictures. Pick one route; you do not need to do both.

## No training: use a ready-made model

For the quickest start:

1. Check `/root/models` on the board for preinstalled models.
2. Open the [MaixHub model zoo](https://maixhub.com/model/zoo), select your board, and find a suitable model.
3. Before downloading, confirm that the description lists your board.

Then follow [Get, Upload and Run a Model](../ai_model_converter/ai_model_deploy.md#upload-the-model). You do not need a dataset or any training.

If you cannot find a suitable model, use the training route below. When using someone else's model, check its license—the author's rules for using, changing, and sharing it.

## Train your own: prepare a starter model

Training usually starts with a model that has already learned general objects. This guide uses the small YOLO11 model `yolo11n.pt`, which is a good first choice.

You normally do not need to download it yourself. The training tool downloads `yolo11n.pt` when training starts, so keep that filename in the command and make sure the computer is online. If automatic download fails, download it from the [Ultralytics YOLO11 model page](https://docs.ultralytics.com/models/yolo11/) and put its path after `model=` in the training command.

`yolo11n.pt` is only the starting point for computer training. It cannot run directly on the board. After training, you will export and convert the result by following [Train a YOLO Detection Model on a Computer](../vision/customize_model_yolo.md).

## Train your own: prepare a dataset

A dataset contains the pictures used for training and the correct answer for each picture. For object detection, each answer says what an object is and where it is.

### Step 1: take pictures

Use the final board to take pictures when possible. The training images will then look more like the camera images the model will see later.

For an apple detector, do not photograph only one red apple in the center of a white table. Include:

- Different types, sizes, and colors of apples.
- Apples near the edge, far away, or partly hidden.
- Different tables, rooms, and lighting.
- Scenes without apples and red objects that might be mistaken for apples.

Start with a small dataset to test the whole process. Add more pictures when you find a situation that fails. Realistic variety matters more than simply collecting a large number of images.

### Step 2: annotate the images

Annotation means drawing a rectangle around every object and giving it a class name.

These tools are free to use:

- [MaixHub online training](../vision/maixhub_train.md): annotate in the browser; the simplest choice for beginners.
- [Make Sense](https://www.makesense.ai/): works in a browser and exports YOLO format.
- [AnyLabeling](https://github.com/vietanhdev/anylabeling): an open-source desktop tool that supports rectangle annotation and assisted labeling.
- [CVAT](https://app.cvat.ai/): offers a free web plan and is useful for larger or team projects.

For computer training, export as **Ultralytics YOLO Detection**. This is a standard way to arrange the image and annotation files; it is not another model.

While annotating:

- Keep each box close to the object's edge.
- If an image contains three apples, draw three boxes.
- Always use the same class name for the same object, such as `apple`.
- Do not leave any target object unmarked.

### Step 3: split training and validation images

Put about 80% of the pictures in the training set and 20% in the validation set:

- **Training set:** pictures the model learns from.
- **Validation set:** separate pictures used to check its progress.

Do not put the same picture in both sets. Nearly identical burst photos should also stay together. Use real pictures from the board in the validation set whenever possible.

### Step 4: use the standard folder layout

Arrange the dataset like this. The locations of `train` and `val` are the important part:

```text
apple_dataset/
├── images/
│   ├── train/       # training images
│   └── val/         # validation images
├── labels/
│   ├── train/       # labels for training images
│   └── val/         # labels for validation images
└── data.yaml
```

The annotation tool creates a `.txt` file with the same name as each image. For example:

```text
images/train/apple_001.jpg
labels/train/apple_001.txt
```

The image and label must have the same base name and be placed in matching `images` and `labels` folders. For a background image with no target object, create an empty `.txt` file with the same base name.

Finally, create `data.yaml` to tell the training tool where the images are and what the classes are called:

```yaml
path: /full/path/to/apple_dataset
train: images/train
val: images/val

names:
  0: apple
```

Replace `path` with the full path to `apple_dataset` on your computer. For more classes, add `1:`, `2:`, and so on in the same order used by the annotation tool.

You can now use [online training on MaixHub](../vision/maixhub_train.md) or [train a YOLO detection model on your computer](../vision/customize_model_yolo.md).

## Using a public dataset

You can search the [Ultralytics dataset list](https://docs.ultralytics.com/datasets/), [Roboflow Universe](https://universe.roboflow.com/), or [Kaggle Datasets](https://www.kaggle.com/datasets).

Before downloading, check its license, confirm that it is an object-detection dataset, and make sure it can be exported as Ultralytics YOLO Detection. Public images can help the training set, but they should not replace board-camera images from the real environment.

## Conversion needs a separate set of pictures

The online converter also asks for 20 to 100 real-scene images. These pictures help the converter adapt the model to the board; they do not train it and do not need annotation.

Put those pictures in a ZIP file. Keep them separate from the training and validation folders. See [Prepare conversion images](../ai_model_converter/online_converter.md#prepare-conversion-images) for the exact requirements.
