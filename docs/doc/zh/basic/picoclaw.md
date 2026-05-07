---
title: MaixCAM / MaixCAM2 使用 PicoClaw
---

## PicoClaw 是什么

[PicoClaw](https://github.com/sipeed/picoclaw) 是 Sipeed 发起的轻量级开源 AI Agent 项目，使用 Go 编写，可以运行在 PC、MaixCAM / MaixCAM2、树莓派、LicheeRV-Nano 等 Linux 设备上。

在 MaixCAM / MaixCAM2 中运行 PicoClaw 后，你可以在 PicoClaw 的对话界面里让它直接操作设备本机，例如创建并运行 MaixPy 脚本、调用摄像头、运行 YOLO 模型、读取检测结果，然后把结果回复给你。

## 使用前准备

1. 让 MaixCAM / MaixCAM2 连接网络。
2. 根据 PicoClaw 官方文档安装适合当前设备架构的 `picoclaw` 可执行文件，参考 [PicoClaw 文档](https://docs.picoclaw.io/)。
3. 按 PicoClaw 文档完成模型供应商、API Key 等配置。

设备架构可以在 MaixCAM / MaixCAM2 终端中查看：

```bash
uname -m
```

配置完成后，可以先在设备上运行一次简单对话确认 PicoClaw 可用：

```bash
picoclaw agent -m "你好，请回复一句话说明你已经在这台设备上运行"
```

也可以使用 PicoClaw 提供的网页或终端界面进行交互，具体以 PicoClaw 官方文档为准。

## 通过 PicoClaw 运行一次人体检测

下面示例的思路是：

1. 你在 PicoClaw 对话界面中提出任务。
2. PicoClaw 在 MaixCAM / MaixCAM2 本机创建一个 MaixPy 脚本。
3. PicoClaw 执行这个脚本。
4. 脚本打开摄像头，使用 YOLO 检测 `person`。
5. 如果检测到人体，脚本打印检测结果并保存一张标注图，PicoClaw 根据输出提醒你。

你可以把下面这段话发给 PicoClaw：


```txt
请参考https://wiki.sipeed.com/maixpy/doc/en/index.html, 在当前创建 /root/picoclaw_person_detect.py, 并执行以下操作:
1. 写入一个 MaixPy 程序：打开摄像头，使用 YOLO 模型检测 person，最多运行 15 秒。
2. 如果检测到 person，请保存标注图到 /root/person_detected.jpg，并输出 PICOCLAW_PERSON_DETECTED、置信度和坐标；如果没有检测到，请输出 PICOCLAW_NO_PERSON。
3. 然后执行 python /root/picoclaw_person_detect.py，并根据输出结果通知我。
```

PicoClaw经过思考后, 生成的脚本如下(注意建议选一些能力强的模型, 否则有可能生成一些错误代码):

```python
from maix import camera, display, image, nn, app, time

MODEL_PATH = "/root/models/yolov5s.mud"
TIMEOUT_MS = 15000
OUT_IMAGE = "/root/person_detected.jpg"

detector = nn.YOLOv5(model=MODEL_PATH, dual_buff=True)
# 如果使用 YOLO11 模型，可以改成：
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

如果 PicoClaw 执行后看到类似输出：

```txt
PICOCLAW_PERSON_DETECTED score=0.86 x=120 y=60 w=80 h=180 image=/root/person_detected.jpg
```

就表示已经检测到人体，并且标注图片保存在 `/root/person_detected.jpg`。

## 模型路径说明

示例默认使用 MaixCAM 常见的模型路径：

```python
MODEL_PATH = "/root/models/yolov5s.mud"
```

如果你的设备是 MaixCAM2，或者系统中已经准备了 YOLO11 模型，可以改成：

```python
MODEL_PATH = "/root/models/yolo11n.mud"
detector = nn.YOLO11(model=MODEL_PATH, dual_buff=True)
```

实际可用模型以设备 `/root/models/` 目录为准。更多 YOLO 用法请看 [YOLO 物体检测](../vision/yolov5.md)。