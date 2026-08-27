---
title: Get, Upload and Run a Model
---

Suppose you want your board to recognize apples on a table. The basic flow is simple: get a model, copy it to the board, run it, and check what it detects.

When the model works on a real camera image, the job is done. Sharing it on MaixHub is optional; it is only a place for other users to download and discuss models.

You do not need to learn every file format before starting. Pick the route that matches your situation.

## Pick a route

- **Just want to try the board:** download a ready-to-use model from the [MaixHub model zoo](https://maixhub.com/model/zoo), choosing your board first.
- **Want to recognize your own objects with the least setup:** use [online training on MaixHub](../vision/maixhub_train.md). The website guides you through taking pictures, drawing boxes, and training.
- **Want to train on your own computer:** follow [Train a YOLO Detection Model on a Computer](../vision/customize_model_yolo.md). It continues through conversion and board testing.
- **Already have a computer-trained model:** use the [online converter](./online_converter.md) to make a board model package.
- **Already downloaded a package made for MaixCAM or MaixCAM2:** skip training and conversion, and continue with [Upload the model](#upload-the-model).

## Prepare the files to upload

After you unzip a model package, keep all files together. Do not rename or delete any of them.

MaixCAM and MaixCAM Pro packages usually contain:

```text
apple.mud
apple.cvimodel
```

MaixCAM2 packages usually contain:

```text
apple.mud
apple_npu.axmodel
apple_vnpu.axmodel
```

Upload all files from the same package. In your code, use the file ending in `.mud`.

## Upload the model

1. Open [MaixVision](https://wiki.sipeed.com/maixvision) and connect the board.
2. Open **Device File Manager** on the right side.
3. Open `/root/models`. This folder is on the board, not on your computer.
4. Upload every file from the same model package.

For example, the model path is:

```text
/root/models/apple.mud
```

## Run the model

If the package includes `main.py`, run it first. Open the file, change the model path to the `.mud` path you uploaded, and click the Run button at the lower left of MaixVision.

If there is no example code, try this YOLO11 object-detection example:

```python
from maix import app, camera, display, image, nn

MODEL = "/root/models/apple.mud"

detector = nn.YOLO11(model=MODEL)
cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
disp = display.Display()

while not app.need_exit():
    img = cam.read()
    objects = detector.detect(img, conf_th=0.5, iou_th=0.45)
    for obj in objects:
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color=image.COLOR_RED)
        name = detector.labels[obj.class_id]
        img.draw_string(obj.x, obj.y, f"{name}: {obj.score:.2f}", color=image.COLOR_RED)
    disp.show(img)
```

If your model is not YOLO11, change only the detector line:

```python
# YOLO26
detector = nn.YOLO26(model=MODEL)

# YOLOv8 or YOLOv5u
detector = nn.YOLOv8(model=MODEL)

# Old YOLOv5
detector = nn.YOLOv5(model=MODEL)
```

`conf_th=0.5` hides results with a score below 0.5. `iou_th=0.45` helps merge duplicate boxes around one object. Keep these values for the first test.

Point the camera at an apple. If the screen shows `apple`, a score, and a box, the model is running.

## Test with new scenes

A model that works on training pictures may still fail in real use. Try a different apple, background, and lighting. Also test a few images without apples.

If it often fails, add pictures of those situations and train again. Converting the same model again will not improve its recognition.

## Optional: share on MaixHub

After the model runs reliably on the board, you can log in to the [MaixHub model zoo](https://maixhub.com/model/zoo) and share it:

1. Choose the correct board model.
2. Upload the complete model package, and preferably the working `main.py`.
3. Describe what it detects, the labels, and suitable distance and lighting.
4. Credit the source and license of any model or data you did not create.
5. Add a picture showing it running on the board.

Models trained online on MaixHub can be shared from the training project without uploading the files again.

## Quick troubleshooting

- **File not found:** check the `.mud` path and make sure the companion files were uploaded.
- **Model will not load:** check that the board selected during download or conversion is correct.
- **Runs but draws no boxes:** check that the model version matches `nn.YOLO...`, then test the original model on your computer.
- **Wrong label names:** check that label order matches the training project.

For models not supported by the online converter, see [manual conversion for MaixCAM2](./maixcam2.md), [manual conversion for MaixCAM](./maixcam.md), or [port an unsupported model](../pro/customize_model.md).
