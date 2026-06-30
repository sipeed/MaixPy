---
title: Convert an ONNX Model to a Model Usable by MaixCAM MaixPy (MUD)
---

> For MaixCAM2 model conversion, see the [MaixCAM2 model conversion documentation](./maixcam2.md)

## Introduction

A model trained on a PC cannot be used directly on MaixCAM, because MaixCAM has limited hardware performance. In most cases, we need to apply `INT8` quantization to reduce computation and convert the model into a format supported by MaixCAM.

This document explains how to convert an ONNX model into a model that MaixCAM can use, namely a **MUD model**.

## Model File Formats Supported by MaixCAM

MUD (**Model Universal Description** file) is a model description format supported by MaixPy. It is used to unify model files across different platforms, making MaixPy code more portable. It is essentially a plain-text file in `ini` format and can be edited with a text editor.

A MUD file is usually accompanied by one or more actual model files. For example, on MaixCAM, the actual model file is in `.cvimodel` format, while the MUD file provides descriptive metadata for it.

## Prepare the ONNX Model

Prepare your ONNX model, then open it in [https://netron.app/](https://netron.app/) to verify that the operators used in your model are supported by the conversion tool. The supported operator list can be found in the **CVITEK_TPU_SDK Development Guide.pdf** from the [Sophgo TPU SDK](https://developer.sophgo.com/thread/473.html).

## Find Suitable Quantized Output Nodes
[See detailed reference here](./onnx_export.md)

Assume the cropped ONNX file you obtained is named `export.onnx`.

## Install the Model Conversion Environment

Model conversion uses Sophgo's [https://github.com/sophgo/tpu-mlir](https://github.com/sophgo/tpu-mlir). We recommend installing it in a Docker environment to avoid host environment incompatibilities. If you are not familiar with Docker, you can think of it as something similar to a virtual machine.

### Pull the Docker Image

```shell
docker pull sophgo/tpuc_dev:latest
```

If pulling the Docker image fails, you can download it this way instead:

```shell
wget https://sophon-file.sophon.cn/sophon-prod-s3/drive/24/06/14/12/sophgo-tpuc_dev-v3.2_191a433358ad.tar.gz
docker load -i sophgo-tpuc_dev-v3.2_191a433358ad.tar.gz
```

This method is referenced from the [official tpu-mlir Docker environment setup](https://github.com/sophgo/tpu-mlir/blob/master/README_cn.md).

You can also configure a domestic mirror in China. You may search for solutions yourself or refer to [Docker proxy setup and domestic mirror acceleration configuration](https://neucrack.com/p/286).

### Run the Container

```shell
docker run --privileged --name tpu-env -v ./:/workspace -it sophgo/tpuc_dev:v3.2
```

First, create a container named `tpu-env`, and mount the current directory to `/workspace` inside the container. This allows file sharing between the host and the container. Please place `export.onnx` in the current directory.

To start the container next time, use:

```shell
docker start tpu-env && docker attach tpu-env
```

### Install tpu-mlir

```shell
pip install tpu_mlir
```

After that, **directly type** `model_transform.py` inside the container and press Enter. If it prints the help information, the installation was successful.

## Convert the ONNX Model to cvimodel

Model conversion mainly uses two commands: `model_transform.py` and `model_deploy.py`. Below is a YOLOv5s example. For other models, adjust the file paths accordingly. **Pay attention to the order of execution.**

`Step 1`

> Note whether the paths for `--model_def`, `--test_result`, `--mlir`, and `--test_input` are consistent with the paths used later. For the other parameters, refer to the table below.

```bash
model_transform.py \
--model_name yolov5s \
--model_def ./export.onnx \
--input_shapes [[1,3,224,320]] \
--mean "0,0,0" \
--scale "0.00392156862745098,0.00392156862745098,0.00392156862745098" \
--keep_aspect_ratio \
--pixel_format rgb \
--channel_format nchw \
--output_names "/model.24/m.0/Conv_output_0,/model.24/m.1/Conv_output_0,/model.24/m.2/Conv_output_0" \
--test_input ./zidane.jpg \
--test_result yolov5s_top_outputs.npz \
--tolerance 0.99,0.99 \
--mlir yolov5s.mlir
```

| Key Parameter | Meaning | Description / Recommendation | Example |
|---|---|---|---|
| `output_names` | Output names of output nodes | These are the output node names mentioned earlier. They must match the actual output names after model export. | `--output_names "output0"` |
| `mean, scale` | Preprocessing used during training | For example, official YOLOv5 preprocessing usually normalizes the 3 RGB channels. By default, you can think of it as `mean=0`, `std=255`, meaning the image pixel values are normalized to a smaller range, so `scale=1/std`. Modify these according to the actual preprocessing of your own model. | `--mean "0,0,0"`，`--scale "0.00392156862745098,0.00392156862745098,0.00392156862745098"` |
| `test_input` | Image used for testing during conversion | For example, `../dog.jpg` is used here, so when actually converting the model, the corresponding test image should be placed near the script directory. Replace it with your own test image according to your model. | `--test_input ./zidane.jpg` |
| `tolerance` | Allowed error before and after quantization | If conversion reports an error saying the error value exceeds this threshold, it means the converted model may differ too much from the ONNX model. If acceptable, you may increase this threshold to allow conversion to pass. However, in most cases, large errors indicate issues in model structure or post-processing, and the model should be optimized with removable post-processing eliminated as much as possible. | `--tolerance 0.99,0.99` |
| `model_def` | The ONNX file after node cropping |  | `--model_def ./export.onnx` |
| `mlir` | The intermediate MLIR file after conversion |  | `--mlir yolov5s.mlir` |
| `test_result` | Intermediate file generated by converting `test_input`, used in later steps |  | `--test_result yolov5s_top_outputs.npz ` |
| `input_shapes` | Input size of the model to be converted | Since the model input image size is fixed, adjust it flexibly according to the image size you plan to use on MaixCAM. This should already be determined during ONNX export. | `--input_shapes [[1,3,224,320]]` |

`Step 2`

> Note whether the paths for `--model_def`, `--test_result`, `--mlir`, and `--test_input` are consistent with the previous step. For other parameters, refer to the table below.  
> The first example is the BF16 conversion process, and the second is the INT8 conversion process. INT8 models require an additional calibration step, so make sure to distinguish between them.

`bf16`

```bash
# export bf16 model
#   not use --quant_input, use float32 for easy coding
model_deploy.py \
--mlir yolov5s.mlir \
--quantize BF16 \
--processor cv181x \
--test_input yolov5s_in_f32.npz \
--test_reference yolov5s_top_outputs.npz \
--model yolov5s_bf16.cvimodel
```

`int8`

```bash
#  "calibrate for int8 model"
# export int8 model
run_calibration.py yolov5s.mlir \
--dataset ./images \
--input_num 1 \
-o yolov5s_cali_table

#  "convert to int8 model"
# export int8 model
#    add --quant_input, use int8 for faster processing in maix.nn.NN.forward_image
model_deploy.py \
--mlir yolov5s.mlir \
--quantize INT8 \
--quant_input \
--calibration_table yolov5s_cali_table \
--processor cv181x \
--test_input yolov5s_in_f32.npz \
--test_reference yolov5s_top_outputs.npz \
--tolerance 0.9,0.6 \
--model yolov5s_int8.cvimodel
```

| Key Parameter | Meaning | Description / Recommendation | Example |
|----------|------|-----------|------|
| `quantize` | Quantized data type | On MaixCAM, `INT8` models are generally preferred. `BF16` models usually offer higher accuracy, but tend to run slower. Therefore, it is recommended to first try converting to `INT8`; if that fails, or if you need higher accuracy and speed is less important, then consider `BF16`. | `--quantize INT8` / `--quantize BF16` |
| `dataset`  | Dataset used for quantization | The dataset is usually placed in the same directory as the conversion script, such as the `images` folder in this example. For YOLOv5, images are generally sufficient, and you can select a subset of representative images from the COCO dataset. `--input_num` specifies how many images are actually used and should be less than or equal to the number of images in the `images` directory. | `--dataset ./images` |
| `mlir`  | MLIR file before conversion | Must match the MLIR file generated by `model_transform.py` | `--mlir yolov5s.mlir` |
| `test_input`  | NPZ file used for testing | Must match the NPZ file generated by the `test_result` parameter in `model_transform.py` | `--test_input yolov5s_in_f32.npz ` |
| `model`  | The final generated cvimodel | Put the generated cvimodel into MaixCAM and configure the MUD file in the same directory so it can be loaded through MaixPy | `--model yolov5s_int8.cvimodel` |

## Write the `mud` File

> Note: the `.mud` file and `.cvimodel` file must be in the same directory.

Here we use a `YOLOv8` model file as an example. There are two files: `yolov8n.mud` and `yolov8n.cvimodel`. The content of the former is:

```ini
[basic]
type = cvimodel
model = yolov8n.cvimodel

[extra]
model_type = yolov8
input_type = rgb
mean = 0, 0, 0
scale = 0.00392156862745098, 0.00392156862745098, 0.00392156862745098
labels = person, bicycle, car, motorcycle, airplane, bus, train, truck, boat, traffic light, fire hydrant, stop sign, parking meter, bench, bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe, backpack, umbrella, handbag, tie, suitcase, frisbee, skis, snowboard, sports ball, kite, baseball bat, baseball glove, skateboard, surfboard, tennis racket, bottle, wine glass, cup, fork, knife, spoon, bowl, banana, apple, sandwich, orange, broccoli, carrot, hot dog, pizza, donut, cake, chair, couch, potted plant, bed, dining table, toilet, tv, laptop, mouse, remote, keyboard, cell phone, microwave, oven, toaster, sink, refrigerator, book, clock, vase, scissors, teddy bear, hair drier, toothbrush
```

| Item | Description |
|------|------|
| Model type | `cvimodel`; for MaixCAM2 it is `axmodel`. |
| Model path | The `yolov8n.cvimodel` file relative to the `mud` file path. |
| `mean` / `scale` | Preprocessing parameters. They must match the preprocessing used for model input during training. |
| `labels` | The list of target categories. Here it corresponds to 80 classes. |
| File placement | In actual use, place the model file and the `mud` file in the same directory. |
| What to modify for a custom model | According to your own model, just modify the `labels` in the `mud` file. |

When actually using this model, just place these two files in the same directory.

According to your own model, you only need to modify the `labels` in the `mud` file.

The `basic` section specifies the model file type and model file path. These are required parameters. With these parameters, the model can be loaded and run using the `maix.nn.NN` class in `MaixPy` or `MaixCDK`.

The `extra` section is designed according to the needs of different models.

For example, in this YOLOv5 case, these parameters are designed mainly for preprocessing, post-processing, labels, and so on. For models already supported by `MaixPy`, you can directly download an existing model and modify it. You can also inspect the actual code, for example the [YOLOv5 source code](https://github.com/sipeed/MaixCDK/blob/71d5b3980788e6b35514434bd84cd6eeee80d085/components/nn/include/maix_nn_yolov5.hpp#L73-L223), to see which parameters are used.

For example, if you trained a `YOLOv5` model to detect digits `0~9`, then you should change `labels` to `0,1,2,3,4,5,6,7,8,9`. If you did not modify the training code, the other parameters can usually remain unchanged.

If you need to port a model not yet supported by `MaixPy`, you can define `extra` according to the model's preprocessing and post-processing requirements, and then write the corresponding decoding class. If you do not want to modify the MaixPy source code in C++, you can also load the model with `maix.nn.NN` in MaixPy, then use `forward` or `forward_image` to get the raw outputs and implement post-processing in Python. However, this is less efficient and generally not recommended.

## Write Post-processing Code

As mentioned in the previous step, if you are just modifying the `mud` file of a model already supported, then you can directly use the corresponding code in `MaixPy` or `MaixCDK` to load it.

If you are supporting a new model, after designing the `mud` file, you need to actually write preprocessing and post-processing. There are two ways:

* Method 1: In MaixPy, use `maix.nn.NN` to load the model, run it with `forward` or `forward_image`, obtain the outputs, and then write post-processing in Python to get the final result.
* Method 2: In `MaixCDK`, refer to the [YOLOv5 source code](https://github.com/sipeed/MaixCDK/blob/71d5b3980788e6b35514434bd84cd6eeee80d085/components/nn/include/maix_nn_yolov5.hpp), add a new `hpp` file, create a class to handle your model, and modify the `@maixpy` annotations for all functions and classes. After implementation, rebuild the `MaixPy` project, and then you can use the new class in `MaixPy` to run your model.

After adding support for a new model, you can also submit the source code as a Pull Request to the main `MaixPy` repository and become a contributor to the `MaixPy` project. You can also share it on [MaixHub](https://maixhub.com/share). Depending on the quality, you may receive a reward ranging from at least `30 RMB` up to `2000 RMB`!
