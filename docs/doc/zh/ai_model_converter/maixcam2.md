---
title: 将 ONNX 模型转换为 MaixCAM2 MaixPy 可以使用的模型（MUD）
---

> MaixCAM / MaixCAM-Pro 模型转换请看[MaixCAM 模型转换文档](./maixcam.md)

## 简介

电脑上训练的模型不能直接给 MaixCAM2 使用，因为 MaixCAM2 的硬件性能有限，一般我们需要将模型进行`INT8`量化以减少计算量，并且转换为 MaixCAM2 支持的模型格式。

本文介绍如何将 ONNX 模型转换为 MaixCAM2 能使用的模型（MUD模型）。


## MaixCAM2 支持的模型文件格式

MUD（模型统一描述文件， model universal description file）是 MaixPy 支持的一种模型描述文件，用来统一不同平台的模型文件，方便 MaixPy 代码跨平台，本身是一个 `ini`格式的文本文件，可以使用文本编辑器编辑。
一般 MUD 文件会伴随一个或者多个实际的模型文件，比如对于 MaixCAM2， 实际的模型文件是`.axmodel`格式， MUD 文件则是对它做了一些描述说明。

这里以 `YOLOv8` 模型文件举例，一共三个文件`yolov8n.mud`， `yolo11n_640x480_vnpu.axmodel`和`yolo11n_640x480_npu.axmodel`，前者内容：

```ini
[basic]
type = axmodel
model_npu = yolo11n_640x480_npu.axmodel
model_vnpu = yolo11n_640x480_vnpu.axmodel

[extra]
model_type = yolo11
type=detector
input_type = rgb
labels = person, bicycle, car, motorcycle, airplane, bus, train, truck, boat, traffic light, fire hydrant, stop sign, parking meter, bench, bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe, backpack, umbrella, handbag, tie, suitcase, frisbee, skis, snowboard, sports ball, kite, baseball bat, baseball glove, skateboard, surfboard, tennis racket, bottle, wine glass, cup, fork, knife, spoon, bowl, banana, apple, sandwich, orange, broccoli, carrot, hot dog, pizza, donut, cake, chair, couch, potted plant, bed, dining table, toilet, tv, laptop, mouse, remote, keyboard, cell phone, microwave, oven, toaster, sink, refrigerator, book, clock, vase, scissors, teddy bear, hair drier, toothbrush

input_cache = true
output_cache = true
input_cache_flush = false
output_cache_inval = true

mean = 0,0,0
scale = 0.00392156862745098, 0.00392156862745098, 0.00392156862745098
```

可以看到， 指定了模型类别为`axmodel`, 模型路径为相对`mud`文件的路径下的`*.axmodel`文件；
以及一些需要用到的信息:
* `labels`: 检测对象的 80 种分类。
* `input_cache`/`output_cache`： 代表着输入输出是否使用缓存内存，使用缓存能在需要多次读取数据的情况下加快读取速度，比如你的后处理需要连续多次读取模型输出结果则建议使用缓冲。
* `input_cache_flush`： 表示运行模型前是不是将 内存 cache 刷新到 DDR 中，一般模型第一层如果是 NPU 算子则必须设置为`true`，对于 YOLO11 因为模型集成了预处理，也就是说第一层是 CPU 处理的，所以设置为了 `false`，如果你不确定则设置为`true`。
* `output_cache_inval`: 表示模型运行完成后是否将输出内存缓冲区设置为无效，保证我们在读取模型输出数据时是直接从 DDR 读取的。一般模型最后一层是 NPU 算子输出则必须设置为`true`，如果是 CPU 算子则可以设置为 `false`减少耗时，如果不确定可以设置为`true`保证数据正确。
* `mean`/`scale`: 实际我们在转模型时将预处理已经集成在模型中，这里只是写着方便看，需要和训练的时候对模型输入的数据的预处理方法一致。

实际用这个模型的时候将三个文件放在同一个目录下即可。


## 准备 ONNX 模型

准备好你的 onnx 模型， 然后在[https://netron.app/](https://netron.app/) 查看你的模型，确保你的模型使用的算子在转换工具的支持列表中，转换工具的支持列表可以在[Pulsar2 工具链文档](https://pulsar2-docs.readthedocs.io/)找到。
对于 `MaixCAM2`，对应了 Pulsar2 文档中 `AX620E` 平台。


## 找出合适的量化输出节点

一般模型都有后处理节点，这部分是 CPU 进行运算的，我们将它们剥离出来，它们会影响到量化效果，可能会导致量化失败。

这里以`YOLOv5 举例`，

![](../../assets/yolov5s_onnx.jpg)

可以看到这里有三个`conv`，后面的计算均由 CPU 进行，我们量化时就采取这几个`conv`的输出作为模型的最后输出，在这里输出名分别叫`/model.24/m.0/Conv_output_0,/model.24/m.1/Conv_output_0,/model.24/m.2/Conv_output_0`。

YOLO11/YOLOv8 请看[离线训练 YOLO11/YOLOv8](../vision/customize_model_yolov8.md).

分类模型一般来说取最后一个输出名称就行，不过如果有`osftmax`的话，建议不把`softmax`包含在模型里面，即取`softmax`前一层的输出名，下图是没有`softmax`层的所以直接取最后一层即可。
![](../../assets/mobilenet_top.png)


## 安装模型转换环境

参考 [Pulsar2 工具链文档](https://pulsar2-docs.readthedocs.io/) 进行安装，要安装它我们直接在 docker 环境中安装，防止我们电脑的环境不匹配，如果你没用过 docker，可以简单理解成它类似虚拟机。

### 安装 docker

参考[docker 安装官方文档](https://docs.docker.com/engine/install/ubuntu/)安装即可。

比如：
```shell
# 安装docker依赖的基础软件
sudo apt-get update
sudo apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common
# 添加官方来源
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
# 安装 docker
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
```


### 拉取 docker 镜像

可以按照 [Pulsar2 工具链文档](https://pulsar2-docs.readthedocs.io/) 中的方法下载和加载，如果文档中不是最新的，也可以到[huggingface](https://huggingface.co/AXERA-TECH/Pulsar2/tree/main) 下载。
即下载镜像文件后，使用命令加载：
```shell
docker load -i pulsar2_vxx.tar.gz
```

工具链会定期更新，下载新的加载即可。

### 运行容器

```shell
docker run -it --privileged --name pulsar2 -v /home/$USER/data:/home/$USER/data pulsar2
```

这就起了一个容器，名叫`pulsar2`，并且把本机的`~/data`目录挂载到了容器的`~/data`，这样就实现了文件共享，并且和宿主机路径一致。

下次启动容器用`docker start pulsar2 && docker attach pulsar2`即可。

在容器中执行`pulsar2` 就可以看到打印的帮助信息就表示可以使用了。

## 转换模型

可以详细读一读 pulsar2 工具的文档。
主要核心就是一个命令：
```shell
pulsar2 build --target_hardware AX620E --input onnx_path --output_dir out_dir --config config_path
```
这里核心就是 `onnx`模型文件和`config`文件了，`onnx`文件在前面提到需要提取节点，可以用脚本`extract_onnx.py`提取：
```python
import onnx
import sys

input_path = sys.argv[1]
output_path = sys.argv[2]
input_names_str = sys.argv[3]
output_names_str = sys.argv[4]
input_names = []
for s in input_names_str.split(","):
    input_names.append(s.strip())
output_names = []
for s in output_names_str.split(","):
    output_names.append(s.strip())

onnx.utils.extract_model(input_path, output_path, input_names, output_names)
```
以及可应用`onnxsim` 简化一下模型。

`config` 文件是一个 `json`配置文件，配置了预处理和输出节点，以及量化策略，具体可以看 pulsar2 文档，比如 yolo11:
```json
{
  "model_type": "ONNX",
  "npu_mode": "NPU2",
  "quant": {
    "input_configs": [
      {
        "tensor_name": "images",
        "calibration_dataset": "tmp_images/images.tar",
        "calibration_size": 64,
        "calibration_mean": [0, 0, 0],
        "calibration_std": [255, 255, 255]
      }
    ],
    "calibration_method": "MinMax",
    "precision_analysis": true
  },
  "input_processors": [
    {
      "tensor_name": "images",
      "tensor_format": "RGB",
      "tensor_layout": "NCHW",
      "src_format": "RGB",
      "src_dtype": "U8",
      "src_layout": "NHWC",
      "csc_mode": "NoCSC"
    }
  ],
  "output_processors": [
    {
      "tensor_name": "/model.23/Concat_output_0",
      "dst_perm": [0, 2, 3, 1]
    },
    {
      "tensor_name": "/model.23/Concat_1_output_0",
      "dst_perm": [0, 2, 3, 1]
    },
    {
      "tensor_name": "/model.23/Concat_2_output_0",
      "dst_perm": [0, 2, 3, 1]
    }
  ],
  "compiler": {
    "check": 3,
    "check_mode": "CheckOutput",
    "check_cosine_simularity": 0.9
  }
}
```

注意到这里`calibration_dataset` 是量化校准数据，从数据集里面抽取一部分即可。

有一个参数需要注意：`npu_mode`，这里是`NPU2`，意思是使用所有NPU算力。
如果你想使用 AI-ISP 功能，需要开启虚拟 NPU 功能将 NPU 分成两个虚拟 NPU，一个给 AI-ISP 用，另一个虚拟 NPU 给我们的模型，即只用一半 NPU 的算力，换成`NPU1`即可。

MaixCAM2 为了方便用户可自由选择是否启用 AI-ISP，所以建议在转模型时两种模型都转换，即对应了 mud 文件中的`model_npu`和 `model_vnpu`两个模型。


## 编写转换脚本

为了方便使用，这里提供几个脚本方便大家使用：
* `extract_onnx.py`: 上面提供的抽取子模型的脚本。
* `gen_cali_images_tar.py`: 从数据集文件夹提取指定数量的图片打包为 `tar` 格式。
```python
import sys
import os
import random
import shutil

images_dir = sys.argv[1]
images_num = int(sys.argv[2])

print("images dir:", images_dir)
print("images num:", images_num)
print("current dir:", os.getcwd())
files = os.listdir(images_dir)
valid = []
for name in files:
    path = os.path.join(images_dir, name)
    ext = os.path.splitext(name)[1]
    if ext.lower() not in [".jpg", ".jpeg", ".png"]:
        continue
    valid.append(path)
print(f"images dir {images_dir} have {len(valid)} images")
if len(valid) < images_num:
    print(f"no enough images in {images_dir}, have: {len(valid)}, need {images_num}")
    sys.exit(1)


idxes = random.sample(range(len(valid)), images_num)
shutil.rmtree("tmp_images", ignore_errors=True)
os.makedirs("tmp_images/images")
for i in idxes:
    target = os.path.join("tmp_images", "images", os.path.basename(valid[i]))
    shutil.copyfile(valid[i], target)
os.chdir("tmp_images/images")
os.system("tar -cf ../images.tar *")
# shutil.rmtree("tmp_images/images")

```

* `convert.sh`: 一键转换脚本，包含了简化 onnx， 提取量化图片数据集，生成 NPU 和 VNPU 两个模型。
```shell
#!/bin/bash

set -e

############# 修改 ####################
model_name=$1
model_path=../../${model_name}.onnx
config_path=yolo11_build_config.json
images_dir=../../images
images_num=100
input_names=images
output_names="/model.23/Concat_output_0,/model.23/Concat_1_output_0,/model.23/Concat_2_output_0"
#############################################

echo "current path: $(pwd)"

# extract and onnxsim
mkdir -p tmp1
onnx_extracted=tmp1/${model_name}_extracted.onnx
onnxsim_path=tmp1/$model_name.onnx
python extract_onnx.py $model_path $onnx_extracted $input_names $output_names
onnxsim $onnx_extracted $onnxsim_path

python gen_cali_images_tar.py $images_dir $images_num

mkdir -p out
tmp_config_path=tmp/$config_path


# vnpu
echo -e "\e[32mBuilding ${model_name}_vnpu.axmodel\e[0m"
rm -rf tmp
mkdir tmp
cp $config_path $tmp_config_path
sed -i '/npu_mode/c\"npu_mode": "NPU1",' $tmp_config_path
sed -i "/calibration_size/c\\\"calibration_size\": ${images_num}," "$tmp_config_path"
pulsar2 build --target_hardware AX620E --input $onnxsim_path --output_dir tmp --config $tmp_config_path
cp tmp/compiled.axmodel out/${model_name}_vnpu.axmodel

# npu all
echo -e "\e[32mBuilding ${model_name}_npu.axmodel\e[0m"
rm -rf tmp
mkdir tmp
cp $config_path $tmp_config_path
sed -i '/npu_mode/c\"npu_mode": "NPU2",' $tmp_config_path
sed -i "/calibration_size/c\\\"calibration_size\": ${images_num}," "$tmp_config_path"
pulsar2 build --target_hardware AX620E --input $onnxsim_path --output_dir tmp --config $tmp_config_path
cp tmp/compiled.axmodel out/${model_name}_npu.axmodel
rm -rf tmp

echo -e "\e[32mGenerate models done, in out dir\e[0m"

```

执行成功后就会得到  `*_npu.axmodel`和`*_vnpu.axmodel`两个模型。


## 编写`mud`文件

根据你的模型情况修改前面提到的`mud`文件，比如对于 YOLO11，修改成你训练的`axmodel`名字和`labels`就好了。

```ini
[basic]
type = axmodel
model_npu = yolo11n_640x480_npu.axmodel
model_vnpu = yolo11n_640x480_vnpu.axmodel

[extra]
model_type = yolo11
type=detector
input_type = rgb
labels = person, bicycle, car, motorcycle, airplane, bus, train, truck, boat, traffic light, fire hydrant, stop sign, parking meter, bench, bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe, backpack, umbrella, handbag, tie, suitcase, frisbee, skis, snowboard, sports ball, kite, baseball bat, baseball glove, skateboard, surfboard, tennis racket, bottle, wine glass, cup, fork, knife, spoon, bowl, banana, apple, sandwich, orange, broccoli, carrot, hot dog, pizza, donut, cake, chair, couch, potted plant, bed, dining table, toilet, tv, laptop, mouse, remote, keyboard, cell phone, microwave, oven, toaster, sink, refrigerator, book, clock, vase, scissors, teddy bear, hair drier, toothbrush

input_cache = true
output_cache = true
input_cache_flush = false
output_cache_inval = true

mean = 0,0,0
scale = 0.00392156862745098, 0.00392156862745098, 0.00392156862745098
```

这里`basic`部分指定了模型文件类别和模型文件路径，是必要的参数，有了这个参数就能用`MaixPy`或者`MaixCDK`中的`maix.nn.NN`类来加载并运行模型了。



如果你需要移植 `MaixPy` 没有支持的模型，则可以根据模型的预处理和后处理情况定义 `extra`, 然后编写对应的解码类。如果你不想用C++修改 MaixPy 源码，你也可以用MaixPy 的`maix.nn.NN`类加载模型，然后用 `forward` 或者 `forward_image` 方法或者原始输出，在 Python 层面写后处理也可以，只是运行效率比较低不太推荐。


## 编写后处理代码

如上一步所说，如果是按照已经支持的模型的`mud`文件修改好，那直接调用`MaixPy`或者`MaixCDK`对应的代码加载即可。
如果是仍未支持的新模型，设计好 `mud` 文件后，你需要实际编写预处理和后处理，有两种方法：
* 一：**适合快速验证**。MaixPy 用 `maix.nn.NN`加载模型，然后`forward`或者`forward_image`函数运行模型，获得输出，然后用 Python 函数编写后处理得到最终结果。可以参考[移植新模型](../pro/customize_model.md)
* 二：**适合正式封装，让`MaixCDK`和`MaixPy`都可以调用而且运行效率更高**。在`MaixCDK`中，可以参考[YOLOv5 的源码](https://github.com/sipeed/MaixCDK/blob/71d5b3980788e6b35514434bd84cd6eeee80d085/components/nn/include/maix_nn_yolov5.hpp), 新增一个`hpp`文件，增加一个处理你的模型的类，并且修改所有函数和类的`@maixpy`注释，编写好了编译`MaixPy`项目，即可在`MaixPy`中调用新增的类来运行模型了。

支持了新模型后还可以将源码提交（Pull Request）到主`MaixPy`仓库中，成为`MaixPy`项目的一员，为社区做贡献，也可以到 [MaixHub 分享](https://maixhub.com/share) 分享你新支持的模型，根据质量可以获得最少 `30元` 最高 `2000元` 的打赏！




