---
title: 模型获取、上板和运行
---

假设你想让板子认出桌上的苹果。你需要准备模型，把模型放到板子，然后运行模型，看看它检测到了什么。

模型能在真实画面中正确检测目标，这条流程就完成了。如果你愿意，还可以把模型分享到 MaixHub，供其他用户下载和交流。

模型是一组训练后生成的文件。这里先不用分辨文件名和格式，只看你想做什么。

## 先选一条路线

- **第一次体验，只想看看板子能识别什么**：到 [MaixHub 模型库](https://maixhub.com/model/zoo)选择自己的板子，下载一个现成模型，然后回到本页继续上传。
- **想让板子识别自己的物品，希望操作尽量简单**：用 [MaixHub 在线训练](../vision/maixhub_train.md)。网页会带你完成拍照、画框和训练，推荐新手选择这条路线。
- **想在自己的电脑上训练**：看 [在电脑训练 YOLO 检测模型](../vision/customize_model_yolo.md)。训练完成后，文档会继续带你转换和上传。
- **电脑上已经有训练结果，但板子还不能运行**：先用[网页转换工具](./online_converter.md)生成板子能用的模型包。
- **已经下载了专门给 MaixCAM 或 MaixCAM2 使用的模型包**：不用训练或转换，直接继续阅读[把模型传到板子](#把模型传到板子)。

## 准备上传的模型文件

模型包解压后会出现几个文件。现在不用研究每种格式，只要把它们放在一起，不要删除或改名。

MaixCAM 和 MaixCAM Pro 的模型包通常包含：

```text
apple.mud
apple.cvimodel
```

MaixCAM2 的模型包通常包含：

```text
apple.mud
apple_npu.axmodel
apple_vnpu.axmodel
```

你只需要记住：上传时把这几个文件一起上传；写代码时选择以 `.mud` 结尾的文件。

## 把模型传到板子

1. 打开 [MaixVision](https://wiki.sipeed.com/maixvision)，连接板子。
2. 打开右侧的“设备文件管理器”。
3. 进入 `/root/models`。这个目录在板子上，不在电脑上。
4. 把同一个模型包里的文件全部上传。

上传后记住 `.mud` 的路径，例如：

```text
/root/models/apple.mud
```

## 运行模型

模型包自带 `main.py` 时，优先运行它。打开文件，把模型路径改成刚才的 `.mud` 路径，然后点击 MaixVision 左下角的运行按钮。

模型包没有示例代码时，可以用下面的 YOLO11 目标检测示例：

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

如果模型不是 YOLO11，只改这一行：

```python
# YOLO26
detector = nn.YOLO26(model=MODEL)

# YOLOv8 或 YOLOv5u
detector = nn.YOLOv8(model=MODEL)

# 旧版 YOLOv5
detector = nn.YOLOv5(model=MODEL)
```

`conf_th=0.5` 表示分数低于 0.5 的结果不显示。`iou_th=0.45` 用于合并同一个物体周围重复的框。第一次运行不用改这两个值。

把摄像头对准苹果。屏幕上出现 `apple`、分数和方框，就说明模型已经跑起来了。

## 用没见过的画面再测一次

训练图片上的效果好，不代表实际使用也好。换一个苹果、背景和光线再测试，并加入几张没有苹果的画面。

如果新画面经常识别失败，回去补充这类图片并重新训练。重复转换同一个模型不会改善识别能力。

## 可选：分享到 MaixHub

确认模型能在板子上稳定运行后，打开 [MaixHub 模型库](https://maixhub.com/model/zoo) 并登录：

1. 进入模型上传或分享入口，选择正确的板子型号。
2. 上传完整模型包，最好同时上传刚刚跑通的 `main.py`。
3. 写清楚模型能识别什么、标签有哪些，以及适合怎样的距离和光线。
4. 如果模型或数据来自别人，注明来源和许可证。许可证是作者写明的使用规则。
5. 加一张板子实际运行的效果图，然后发布。

在 MaixHub 在线训练的模型可以从训练项目直接“分享到模型库”，不用重新上传文件。

## 出错时先查这几项

- **提示找不到文件**：检查代码里的 `.mud` 路径，并确认配套模型文件也已上传。
- **模型无法加载**：检查下载或转换时选择的板子型号。
- **能运行但没有方框**：检查模型版本是否对应正确的 `nn.YOLO...`，再用电脑测试原始模型。
- **类别名称不对**：检查标签顺序是否和训练时一致。

网页转换不支持的模型才需要进入进阶文档：[手动转换给 MaixCAM2](./maixcam2.md)、[手动转换给 MaixCAM](./maixcam.md)或[移植 MaixPy 尚未支持的模型](../pro/customize_model.md)。
