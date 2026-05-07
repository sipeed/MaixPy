---
title: Using PicoClaw with MaixCAM / MaixCAM2
---

## What Is PicoClaw

[PicoClaw](https://github.com/sipeed/picoclaw) is a lightweight open-source AI Agent project initiated by Sipeed. It is written in Go and can run on PCs, MaixCAM / MaixCAM2, Raspberry Pi, LicheeRV-Nano, and other Linux devices.

After PicoClaw is running on MaixCAM / MaixCAM2, you can ask it from the PicoClaw conversation UI to operate the device itself, such as creating and running MaixPy scripts, opening the camera, running a YOLO model, reading the detection result, and replying to you.

## Preparation

1. Connect MaixCAM / MaixCAM2 to the network.
2. Install the `picoclaw` executable for the current device architecture according to the official PicoClaw documentation. See [PicoClaw documentation](https://docs.picoclaw.io/).
3. Configure the model provider, API key, and other PicoClaw settings according to the PicoClaw documentation.

You can check the device architecture in the MaixCAM / MaixCAM2 terminal:

```bash
uname -m
```

After configuration, run a simple test on the device:

```bash
picoclaw agent -m "Hello, reply with one sentence to confirm you are running on this device."
```

You can also use the web UI or terminal UI provided by PicoClaw. Follow the PicoClaw documentation for the exact usage.

## Run One Person Detection Through PicoClaw

The workflow of this example is:

1. You send a task in the PicoClaw conversation UI.
2. PicoClaw creates a MaixPy script on the MaixCAM / MaixCAM2 device.
3. PicoClaw runs the script.
4. The script opens the camera and uses YOLO to detect `person`.
5. If a person is detected, the script prints the detection result and saves an annotated image. PicoClaw then replies to you according to the output.

You can send this prompt to PicoClaw:

```txt
Refer to https://wiki.sipeed.com/maixpy/doc/en/index.html, create /root/picoclaw_person_detect.py on the current device, and do the following:
1. Write a MaixPy program: open the camera, use a YOLO model to detect person, and run for at most 15 seconds.
2. If person is detected, save the annotated image to /root/person_detected.jpg, and output PICOCLAW_PERSON_DETECTED, confidence, and coordinates; if no person is detected, output PICOCLAW_NO_PERSON.
3. Then run python /root/picoclaw_person_detect.py and notify me according to the output.
```

After thinking, PicoClaw generates a script like the following. It is recommended to choose a capable model; otherwise, it may generate incorrect code:

```python
from maix import camera, display, image, nn, app, time

MODEL_PATH = "/root/models/yolov5s.mud"
TIMEOUT_MS = 15000
OUT_IMAGE = "/root/person_detected.jpg"

detector = nn.YOLOv5(model=MODEL_PATH, dual_buff=True)
# To use a YOLO11 model, change it to:
# detector = nn.YOLO11(model="/root/models/yolo11n.mud", dual_buff=True)

cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
disp = display.Display()

start = time.ticks_ms()
detected = False

while not app.need_exit():
    img = cam.read()
    objs = detector.detect(img, conf_th=0.5, iou_th=0.45)

    for obj in objs:
        class_name = detector.labels[obj.class_id]
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color=image.COLOR_RED)
        img.draw_string(obj.x, obj.y, f"{class_name}: {obj.score:.2f}", color=image.COLOR_RED)

        if class_name == "person":
            img.save(OUT_IMAGE)
            print(
                "PICOCLAW_PERSON_DETECTED "
                f"score={obj.score:.2f} "
                f"x={obj.x} y={obj.y} w={obj.w} h={obj.h} "
                f"image={OUT_IMAGE}"
            )
            detected = True
            break

    disp.show(img)

    if detected:
        break
    if time.ticks_ms() - start > TIMEOUT_MS:
        break

if not detected:
    print(f"PICOCLAW_NO_PERSON timeout_ms={TIMEOUT_MS}")
```

If PicoClaw sees output similar to:

```txt
PICOCLAW_PERSON_DETECTED score=0.86 x=120 y=60 w=80 h=180 image=/root/person_detected.jpg
```

it means a person was detected, and the annotated image is saved to `/root/person_detected.jpg`.

## Model Path

The example uses the common MaixCAM model path by default:

```python
MODEL_PATH = "/root/models/yolov5s.mud"
```

If you are using MaixCAM2, or if a YOLO11 model is already available on your system, change it to:

```python
MODEL_PATH = "/root/models/yolo11n.mud"
detector = nn.YOLO11(model=MODEL_PATH, dual_buff=True)
```

The actual model path depends on the files in `/root/models/` on your device. For more YOLO usage, see [YOLO object detection](../vision/yolov5.md).
