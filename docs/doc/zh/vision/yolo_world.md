---
title: MaixPy MaixCAM2 使用 YOLO World 模型实现无需训练检测任意目标
---

## YOLO World 硬件平台支持情况

| 硬件平台 | 是否支持 |
| -------- | -------- |
| MaixCAM | 否      |
| MaixCAM2 | 是      |


## 回顾 YOLO 目标检测

YOLO 大家都很熟悉，即一个适合边缘设备部署的目标检测模型，可以快速检测到训练好的目标。
比如我们想检测画面中`苹果`的位置，需要先采集`苹果`的图像数据，然后训练出一个模型，最后导出模型在 MaixPy 中使用这个模型进行检测。

也就是说每有一个想检测的目标，就需要重新训练一个模型，这个过程比较繁琐而且需要训练时间，最重要的是不能在端测进行训练，必须在有 GPU 的电脑或服务器训练。

## YOLO World 概念

YOLO World 则不需要额外的训练，只需要告诉模型我们想检测的目标是什么，YOLO World 就可以检测到这个目标，听起来是不是很神奇。

YOLO World 是一个新的概念，YOLO World 是一个可以检测任意目标的模型，YOLO World 通过`Prompt`的方式来实现这个功能。
即在模型中加入了语言模型的能力，通过输入文字描述来告诉模型我们想检测的目标是什么。
比如我们要检测`苹果`，只需要输入`apple`和要检测的图像，模型就可以检测到图像中的`苹果`坐标。

此处不阐述更具体的专业知识，有兴趣学习请参考 [YOLO World 官方仓库](https://github.com/AILab-CVC/YOLO-World)。

## MaixPy 中使用 YOLO World

### MaixPy 中的 YOLO World 实现

MaixPy 移植了[ultralytics](https://github.com/ultralytics/ultralytics/blob/main/docs/en/models/yolo-world.md) 即 YOLOv8/YOLO11 官方移植的 YOLO World 模型，使用了[ONNX-YOLO-World-Open-Vocabulary-Object-Detection](https://github.com/AXERA-TECH/ONNX-YOLO-World-Open-Vocabulary-Object-Detection)这个项目。
所以如果你想在 PC 上体验（**注意不是运行在 MaixCAM**)，可以按照这个文档体验。比如我们可以：

先指定要检测的目标分类，保存一个只能检测我们指定目标的模型：
```python
from ultralytics import YOLO

model = YOLO("yolov8s-world.pt")  # or select yolov8m/l-world.pt
model.set_classes(["person", "bus"])
model.save("custom_yolov8s.pt")
```

再使用新的模型执行检测：
```python
from ultralytics import YOLO

model = YOLO("custom_yolov8s.pt")
results = model.predict("path/to/image.jpg")
results[0].show()
```

### 原理介绍

上面可以看到先指定检测的目标分类得到一个新的模型，然后使用这个模型进行检测。

原理如下：
由于边缘计算硬件的性能和功耗限制，我们把 YOLO World 模型（前面提到的`yolov8s-world.pt`）内部分成了两部分：
* **语言文字模型(text_feature model)**：通过运行这个模型，将语言文字(`Prompt`）预先编码成一个文本特征向量（可以简单理解一个数组），存储在一个`.bin`文件中。这个模型比较大，运行缓慢。
* **检测模型(yolo model)**：通过运行这个模型，将图像和特征向量(`.bin`)同时作为输入，进行目标检测，输出检测到的目标坐标和分类名称。这个模型比较小，运行速度快。

分成两个部分的原因是我们实际在检测的时候只需要检测模型，无需每次都运行语言模型，节省了运行时间和功耗。
比如我们要检测`苹果`，只需要运行一次语言模型（占用资源大），将`apple`编码成特征向量（很小的文件），存储在文件中，然后每次检测的时候只需要运行检测模型，将图像和特征向量结合起来进行检测。
当我们需要检测新的目标的时候再运行一次语言模型生成新的特征向量文件即可。

所以在前面的例子中，电脑上使用的`yolov8s-world.pt`一个模型文件包含了语言模型和检测模型，为了方便边缘设备使用，我们把它拆分成了两个模型文件：
* `yolo-world_4_class.mud`：检测模型，运行速度快，体积小。
* `yolo-world_text_feature_4_class.mud`：语言模型，运行速度慢，体积大。


### 运行语言模型指定要检测的目标

运行一次语言模型，指定要检测的目标，生成特征向量文件，注意这段代码可以在 MaixCAM2 或者 电脑上运行。

建议先在终端执行 `pip install -U yolo-world-utils` 或者 `Python` 运行`import os;os.system("pip install -U yolo-world-utils")`先安装并更新工具。
> 这一步是安装工具软件，第一次运行会提示需要下载一个 onnx 模型文件到某个路径，可以到[这里](https://github.com/Neutree/yolo-world-utils/releases) 手动下载放到提示的路径。
> 如果你在这一步遇到了困难，也可以先跳过此步骤，用内置的`/root/models/yolo-world_4_class_person.txt` 和 `/root/models/yolo-world_4_class_person.bin`两个文件继续尝试后面的步骤，再慢慢解决问题。

再执行：
```python
import os

labels = ["apple", "banana", "orange", "grape"]
out_dir = "/root/models"
name = "yolo-world_4_class_my_feature"

feature_file = os.path.join(out_dir, f"{name}.bin")
labels_file = os.path.join(out_dir, f"{name}.txt")
with open(labels_file, "w") as f:
    for label in labels:
        f.write(f"{label}\n")

cmd = f"python -u -m yolo_world_utils gen_text_feature --labels_path {labels_file} --out_feature_path {feature_file}"

print(f"Now run\n\t`{cmd}`\nto generate text feature of\n{labels}")
print("\nplease wait a moment, it may take a few seconds ...\n")
ret = os.system(cmd)
if ret != 0:
    print("[ERROR] execute have error, please see log")
else:
    print(f"saved\n\tlabels to:\n\t{labels_file}\n and text feature to:\n\t{feature_file}")
    print(f"please use yolo-world_{len(labels)}_class.mud model to run detect")
```

这里我们指定了要检测 4 个分类，设置`labels`就可以了，会生成检测需要的两个文件(`*.bin`和`*.txt`)。
**注意**：`labels`格式要求：
* 每个分类名称必须是**英文**，不能是中文或其它语言的单词，因为语言模型只支持英文。
* 可以多个单词，但是长度不能太长，使用BPE编码后的长度最长为 75 个token，简单来说如果太长会报错，试一试就知道了。


### 运行检测模型

前面我们生成了特征向量，现在我们已经有三个文件：
1. 文本特征向量`yolo-world_4_class_my_feature.bin`。
2. 标签文本文件`yolo-world_4_class_my_feature.txt`。
3. 1 分类检测模型`yolo-world_4_class.mud`，内置在`/root/models`目录下。
> 注意这里检测模型为`4_class`，即只能检测 4 个分类的目标，那么 `.txt` 里面只能有四个分类，要一一对应。比如1分类要用`yolo-world_1_class.mud`模型，`.txt`里面也要有 1 行分类名称。
> 系统在`/root/models`目录下内置了`1/4`种分类的检测模型，分别为`yolo-world_1_class.mud`，`yolo-world_4_class.mud`。如果你需要检测其它数量的分类，请按照下面的**下载更多分类数量的检测模型**下载对应的模型文件。
> 建议在文件名命名时加上分类数量防止弄混淆，比如`yolo-world_4_class.mud`，`yolo-world_4_class_my_feature.bin`，`yolo-world_4_class_my_feature.txt`。

我们就可以直接使用 YOLO World 模型进行实时目标检测了，代码基本和 YOLOv8 和 YOLO11 一样：

```python
detector = nn.YOLOWorld("/root/models/yolo-world_4_class.mud",
                        "/root/models/yolo-world_4_class_my_feature.bin",
                        "/root/models/yolo-world_4_class_my_feature.txt",
                        dual_buff = True)

cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
disp = display.Display()

while not app.need_exit():
    img = cam.read()
    objs = detector.detect(img, conf_th = 0.5, iou_th = 0.45)
    for obj in objs:
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color = image.COLOR_RED)
        msg = f'{detector.labels[obj.class_id]}: {obj.score:.2f}'
        img.draw_string(obj.x, obj.y, msg, color = image.COLOR_RED)
    disp.show(img)
```

## 下载更多分类数量的检测模型

系统内默认提供了 1/4 分类的检测模型，提供了两种方式：

### 到 MaixHub 模型库下载

到[MaixHub 模型库]()下载更多分类（支持哪些分类数量可以看其介绍文档）。
比如只少提供了`2/3`分类数量的模型。


### 自己生成模型

如果内置和 MaixHub 都找不到你需要的分类数量，那就需要自己生成了，方法如下：
> 如果你自己没有环境或能力完成，可以到 QQ 群 86234035 或者 [telegram](https://t.me/maixpy) 请求有能力的群友有偿帮忙转。

提供了 docker 镜像，拉取镜像到本地运行即可生成任意分类的模型。
* 首先保证能正常从 dockerhub 拉取镜像文件，最好设置代理，可以参考[docker 设置代理](https://neucrack.com/p/286)。
* 可以用`docker pull hello-world`测试是否能成功。
* `docker pull sipeed/yolo-world-generator-maixcam2`
> `sipeed/sipeed/yolo-world-generator-maixcam2`依赖了 `sipeed/pulsar2`镜像，会自动下载，另外你也可以在[pulsar2官方网站](https://pulsar2-docs.readthedocs.io/zh-cn/latest/user_guides_quick/quick_start_prepare.html)手动下载镜像文件，然后加载镜像并重命名
> * `docker load -i *.tar.gz`
> * `docker tag pulsar2:3.3 sipeed/pulsar2:latest`，这里`3.3`根据具体版本更改。
* `docker run -it --rm -v ${PWD}/out:/root/out sipeed/yolo-world-generator-maixcam2 /bin/bash`
这里`-v ${PWD}/out:/root/out` 是将当前目录的 `out`文件夹映射到容器里面，容器生成的文件就可以在当前目录看到了（多个映射目录重复多个`-v src:dst`参数就好了）。
另外如果你想替换量化图片，也可以映射目录到`/root/images`目录，不设置则使用默认的300张图量化。
如果想替换量化的文本(比如你需要很多分类，默认的80种分类可能不够用来量化，也许会造成量化误差)，映射目录到`/root/data`，`data`目录里面放一个`labes.txt`，每行一个类别名即可，不设置则使用默认内置的 coco 80 分类名。

就会进入 docker 容器内部了，执行转换命令即可：
```shell
cd /root
./gen_model.sh 1 640 480
```
这里三个参数：
* class_num: 即分类数量。
* width: 输入分辨率宽度。
* height: 输入分辨率高度。
* 生成完成后在 out 目录下会有模型文件压缩包，解压即可使用。

生成模型需要的时间比较久，需要耐心等待。


### 其它参考

如果你想更深入了解移植过程，可以看[再谈 YOLO World 部署](https://zhuanlan.zhihu.com/p/721856217)




