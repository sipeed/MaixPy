---
title: Manually Convert for MaixCAM2
---

> For MaixCAM / MaixCAM-Pro model conversion, please refer to the [MaixCAM Model Conversion Documentation](./maixcam.md)

> This is an advanced guide. For a common YOLO detection model, use the [online converter](./online_converter.md) first. It does not require Docker. Continue here only when the online converter does not support the model or you need custom settings.

## Introduction

Models trained on a computer cannot be used directly on MaixCAM2. They generally need to be quantized to INT8 and converted to the `.axmodel` format supported by MaixCAM2. INT8 can typically reduce model storage, memory bandwidth, and runtime overhead, although actual speed also depends on the model architecture, input size, and amount of output data.

This page is intended for readers who are familiar with Python and Docker and can inspect ONNX inputs and outputs with Netron. The complete example applies only to **standard Ultralytics YOLO11 Detect**.

Note: If you run into a conversion problem and ask for help in a QQ group, on the forum, or on GitHub, do not merely say “Why did the conversion fail?” and attach a screenshot of the error. Include the model type, input size, number of classes, ONNX input and output nodes and their shapes, the complete conversion command or configuration file, the conversion tool and MaixPy versions, and the complete log from the start of conversion through the error. This information helps others diagnose the problem accurately.

## Supported Model File Format for MaixCAM2

MUD (Model Universal Description) is a model description file supported by MaixPy that unifies models across different platforms, making MaixPy code cross-platform. It is a text file in `ini` format and can be edited with a text editor.
A MUD file is usually accompanied by one or more actual model files. For MaixCAM2, the actual model files use the `.axmodel` format, while the MUD file describes them. This page will produce:

```text
yolo11n.mud
yolo11n_npu.axmodel
yolo11n_vnpu.axmodel
```

Follow the steps below to convert an ONNX file into a MUD model that can run on MaixCAM2.

## Prepare the ONNX Model

The goal of this section is to obtain a `.onnx` file that Pulsar2 can read. ONNX usually comes from one of these sources:

1. **Exported after training**: after training YOLO11 / YOLOv8 and obtaining a `.pt` file, follow [Train a YOLO Detection Model on a Computer](../vision/customize_model_yolo.md). For MaixCAM2, use a fixed input size such as `640x480` or `320x240`; do not use dynamic input shapes.
2. **Exported from another framework**: for example, PyTorch or TensorFlow. Make sure the exported ONNX has a fixed input shape and can be opened in Netron.
3. **Provided by a third party**: you can start from the ONNX file directly, but you need to confirm that the license allows usage and that the model structure is suitable for MaixCAM2.

If `.mud` and `.axmodel` files are already available, the model has already been converted for MaixCAM2 and can be deployed directly. This conversion flow is not required.

Place the ONNX file in a separate working directory and name it `model.onnx`. Then open it with [Netron](https://netron.app/) and record the following information:

| Item | Verification method | Subsequent use |
| --- | --- | --- |
| Input node name | Check the input node area in Netron; a common name is `images` | Input parameter for the ONNX extraction command and `tensor_name` in `config.json` |
| Input shape | Check the input node shape in Netron, for example `1x3x480x640` | Used to confirm that export size and MaixPy runtime input size match |
| Candidate output nodes | Check the final output nodes before post-processing | Output parameters for the ONNX extraction command and `output_processors` in `config.json` |

Also confirm that the model operators are supported by Pulsar2. MaixCAM2 corresponds to the `AX620E` platform in Pulsar2. If conversion reports an unsupported operator, adjust the model structure during training/export, or use a model structure already supported by MaixPy.

## Find Appropriate Quantization Output Nodes

The goal of this section is to generate `export.onnx`, which is used by the conversion command later.

Many detection models contain post-processing nodes at the end of the ONNX graph. These nodes are usually better handled by CPU code. Quantizing the full ONNX may increase quantization error or cause conversion failure, so first choose suitable output nodes and extract a smaller ONNX.

Use the following table to select output nodes for common model types. For classification and other models, see the [ONNX Node Trimming Tutorial](./onnx_export.md).

| Model type | Recommended output node choice | Next step |
| --- | --- | --- |
| YOLO11 / YOLOv8 detection | For MaixCAM2, use the `/model.xx/Concat...` output nodes and leave decoding / NMS to MaixPy post-processing | Use the common node table below |
| YOLO11 / YOLOv8 pose / seg / obb | These models have more output nodes | Confirm the nodes in the task-specific guide, then follow the trimming tutorial |
| Classification model | Use the final classification output; if the graph ends with `softmax`, use the output before `softmax` | Record that node name |

Common MaixCAM2 output nodes for YOLO detection:

| Model | Recommended output nodes |
| --- | --- |
| YOLOv8 detection | `/model.22/Concat_1_output_0`<br>`/model.22/Concat_2_output_0`<br>`/model.22/Concat_3_output_0` |
| YOLO11 detection | `/model.23/Concat_output_0`<br>`/model.23/Concat_1_output_0`<br>`/model.23/Concat_2_output_0` |

If your node names are not exactly the same, use Netron to find nodes at the same position and with the same meaning instead of copying the names mechanically.

For standard YOLO11 / YOLOv8 Detect models, MaixPy's three-output mode requires each level to have this number of channels:

```text
64 + C
```

Here, 64 is the default number of DFL regression channels and `C` is the number of classes. For an `H×W` input, select three four-dimensional NCHW outputs:

```text
[1, 64+C, H/8,  W/8]
[1, 64+C, H/16, W/16]
[1, 64+C, H/32, W/32]
```

For example, for the `640×480`, 80-class model used in this page, the three outputs must be:

```text
[1, 144, 60, 80]
[1, 144, 30, 40]
[1, 144, 15, 20]
```

Node names in common exports may contain `/model.23/Concat...`, but the same names can refer to entirely different tensors when the Ultralytics version or export method changes. Do not copy node names mechanically: the number of outputs, rank, and shapes must all match the requirements above.

For example, the following aggregated three-dimensional outputs:

```text
[1, 64, N]
[1, C, N]
[1, 4, N]
```

are clearly not the three feature maps required by this page. Applying the four-dimensional `dst_perm = [0,2,3,1]` to these three-dimensional outputs causes a dimension error. Even if you switch to a three-dimensional permutation and allow compilation to continue, MaixPy's YOLO11 three-output mode will still fail because the shapes do not match.

After confirming the input node name and output node names, install the tools needed for extraction and simplification:

```bash
pip install onnx onnxsim
```

Then run:

```bash
python -c "import onnx,sys; onnx.utils.extract_model(sys.argv[1], sys.argv[2], [s.strip() for s in sys.argv[3].split(',')], [s.strip() for s in sys.argv[4].split(',')])" model.onnx tmp_extract.onnx "images" "/model.23/Concat_output_0,/model.23/Concat_1_output_0,/model.23/Concat_2_output_0"
onnxsim tmp_extract.onnx export.onnx
```

Replace:

* `model.onnx` with your original ONNX file name.
* `"images"` with the input node name shown in Netron.
* `"/model.23/Concat_output_0,...` with your selected output node names, separated by English commas.

After the command succeeds, `export.onnx` is generated in the current directory. All later `--input ./export.onnx` commands refer to this extracted and simplified ONNX file.

## Install the Model Conversion Environment

Follow the [Pulsar2 Toolchain Documentation](https://pulsar2-docs.readthedocs.io/) to install it. Use Docker to avoid host environment conflicts. If you're new to Docker, think of it as a lightweight virtual machine.

### Install Docker

Follow [Docker's official documentation](https://docs.docker.com/engine/install/ubuntu/). After installation, run the following command. If it prints a version number, Docker is ready:

```shell
docker --version
```

Example:

```shell
# Install Docker dependencies
sudo apt-get update
sudo apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common
# Add Docker repo
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
# Install Docker
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
```

### Load the Docker Image

Follow the instructions in the [Pulsar2 Documentation](https://pulsar2-docs.readthedocs.io/), or download the image from [Hugging Face](https://huggingface.co/AXERA-TECH/Pulsar2/tree/main) / [ModelScope](https://www.modelscope.cn/models/AXERA-TECH/Pulsar2/files).

After downloading `pulsar2_vxx.tar.gz`, load it with:

```shell
docker load -i pulsar2_vxx.tar.gz
```

Then check the actual image name:

```shell
docker images | grep pulsar2
```

### Run the Container

Enter your model conversion work directory and run the container. Replace `pulsar2:6.0` with the image name shown by `docker images` if yours is different:

```shell
mkdir -p ~/maixcam2_convert
cd ~/maixcam2_convert
docker run -it --net host --rm -v "$PWD":/data -w /data pulsar2:6.0
```

Inside the container, the current directory is `/data`. Put `export.onnx`, `datasets/train.tar`, and `config/*.json` in this directory for the following steps.

## Convert the Model

Before running `pulsar2 build`, prepare these files in the working directory:

| File | Purpose |
| --- | --- |
| `export.onnx` | The extracted and simplified ONNX from the previous step |
| `datasets/train.tar` | Calibration image package for INT8 quantization |
| `config/yolo11n.npu.json` | Configuration for the full NPU model |
| `config/yolo11n.vnpu.json` | Configuration for the virtual NPU model |

To create the calibration package, put 20 to 100 representative real-scene images into `datasets/train_images`, then run:

```bash
mkdir -p datasets/train_images
# Put 20 to 100 representative images into datasets/train_images first.
tar -cf datasets/train.tar -C datasets/train_images .
```

The main Pulsar2 command is:

```shell
pulsar2 build --target_hardware AX620E --input onnx_path --output_dir out_dir --config config_path
```

The parameters should be filled as follows:

| Parameter | Value |
| --- | --- |
| `--target_hardware AX620E` | Fixed for MaixCAM2 |
| `--input onnx_path` | The extracted ONNX, for example `./export.onnx` |
| `--output_dir out_dir` | Temporary output directory, for example `./tmp` |
| `--config config_path` | Conversion config file, for example `./config/yolo11n.npu.json` |

For YOLO11 detection, create `config/yolo11n.npu.json` first. The important fields are:

```json
{
  "model_type": "ONNX",
  "npu_mode": "NPU2",
  "quant": {
    "input_configs": [
      {
        "tensor_name": "images",
        "calibration_dataset": "datasets/train.tar",
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

Then copy it to `config/yolo11n.vnpu.json` and change only:

```shell
cp config/yolo11n.npu.json config/yolo11n.vnpu.json
```

```json
"npu_mode": "NPU1"
```

`NPU2` uses the full NPU and should be written to `model_npu` in the `.mud` file. `NPU1` leaves resources for AI-ISP / virtual NPU usage and should be written to `model_vnpu`.

Run the conversion commands:

```shell
pulsar2 build --target_hardware AX620E --input ./export.onnx --output_dir ./tmp --config ./config/yolo11n.npu.json
mkdir -p out
cp tmp/compiled.axmodel out/yolo11n_npu.axmodel

rm -rf tmp
pulsar2 build --target_hardware AX620E --input ./export.onnx --output_dir ./tmp --config ./config/yolo11n.vnpu.json
cp tmp/compiled.axmodel out/yolo11n_vnpu.axmodel
```

After successful execution, `out/` contains `yolo11n_npu.axmodel` and `yolo11n_vnpu.axmodel`.

## Write the `mud` File

Create `out/yolo11n.mud` in the same directory as the two `.axmodel` files:

```ini
[basic]
type = axmodel
model_npu  = yolo11n_npu.axmodel
model_vnpu = yolo11n_vnpu.axmodel

[extra]
model_type = yolo11
type=detector
input_type = rgb
labels = your_label_0,your_label_1,your_label_2

input_cache = true
output_cache = true
input_cache_flush = false
output_cache_inval = true

mean = 0,0,0
scale = 0.00392156862745098, 0.00392156862745098, 0.00392156862745098
```

Replace `labels` with the class names used during training, and keep their order exactly the same as the training dataset. The `[basic]` section is required; once it is correct, MaixPy can load the model through the `.mud` file.

## Deploy to the Device and Verify Quickly

MaixPy usually loads the `.mud` file. The `.mud` file then points to the actual `.axmodel` files. The simplest approach is to put them in the same directory, for example:

```text
/root/models/my_model.mud
/root/models/my_model_npu.axmodel
/root/models/my_model_vnpu.axmodel
```

Then first confirm that the model can be loaded:

```python
from maix import nn

model = nn.NN("/root/models/my_model.mud")
print(model)
```

If the model type is already supported by MaixPy, prefer the wrapped API. For example, for YOLO, see the [YOLO object detection documentation](../vision/yolov5.md):

```python
from maix import nn

detector = nn.YOLO11(model="/root/models/yolo11n.mud", dual_buff=True)
```

## Debug Checklist

If the model cannot be loaded or the result is wrong, check these items first:

1. Whether the `.mud` and `.axmodel` files are in the same directory, and whether `model_npu` and `model_vnpu` in the `.mud` file use the correct file names.
2. Whether the path used on the device really exists, such as `/root/models/xxx.mud`.
3. Whether `labels` exactly matches the class count and class order used during training.
4. Whether `model_type` is supported by MaixPy, such as `yolo11`, `yolov8`, or `classifier`.
5. Whether input resolution, `mean`, `scale`, and RGB/BGR order match training, export, and conversion settings.
6. Whether the ONNX output nodes exactly match `output_processors` in `config.json`.
7. If you are not sure whether the problem is the model or your code, test with a MaixHub model or a built-in model first. After an official model runs correctly, debug your own model.

When asking for help, provide the ONNX export command, model task and class count, input and output names and shapes, complete conversion command, tool versions, MUD file, MaixPy / system version, and complete error log.

After these basic checks pass, continue with the specific model documentation or conversion workflow. If this is a model type not yet wrapped by MaixPy, continue with the next section.

## Write Post-processing Code

If the model type is already supported by MaixPy, such as YOLO or a classifier, you usually do not need to write post-processing manually. Use the corresponding MaixPy API directly.

If MaixPy does not yet wrap your model type, implement post-processing according to the model outputs and choose one of these paths:

* **Quick verification**: use `maix.nn.NN` to load the `.mud` file, call `forward` or `forward_image`, and write post-processing in Python. See [Porting a New Model](../pro/customize_model.md) for the full workflow.
* **Formal integration**: add a model decoding class in `MaixCDK` so both `MaixCDK` and `MaixPy` can use it with better performance. You can refer to the [YOLOv5 source code](https://github.com/sipeed/MaixCDK/blob/71d5b3980788e6b35514434bd84cd6eeee80d085/components/nn/include/maix_nn_yolov5.hpp), add the corresponding `hpp` file, complete the `@maixpy` annotations, and rebuild MaixPy.

After adding support for a new model, you can submit a Pull Request to the main `MaixPy` repository or share your model on [MaixHub](https://maixhub.com/share).
