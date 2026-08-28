---
title: Manually Convert for MaixCAM
---

> For MaixCAM2 model conversion, see the [MaixCAM2 model conversion documentation](./maixcam2.md)

> This is an advanced guide. For a common YOLO detection model, use the [online converter](./online_converter.md) first. It does not require Docker. Continue here only when the online converter does not support the model or you need custom settings.

## Introduction

A model trained on a PC cannot be used directly on MaixCAM / MaixCAM-Pro. It must first be converted to the `.cvimodel` format supported by the device, with a matching `.mud` model description file. This page uses a YOLOv8 detection model as an example and walks through the complete ONNX-to-MaixCAM conversion flow.

This page is intended for readers who are familiar with Python and Docker and can inspect ONNX inputs and outputs with Netron. The complete workflow uses only a YOLOv8 detection model as its example.

Note: If you run into a conversion problem and ask for help in a QQ group, on the forum, or on GitHub, do not merely say “Why did the conversion fail?” and attach a screenshot of the error. Include the model type, input size, number of classes, ONNX input and output nodes and their shapes, the complete conversion command or configuration file, the conversion tool and MaixPy versions, and the complete log from the start of conversion through the error. This information helps others diagnose the problem accurately.

## Model File Formats Supported by MaixCAM

MUD (Model Universal Description) is a model description file supported by MaixPy. It unifies model loading across different platforms. It is essentially a plain-text `ini` file and can be edited with a text editor.

For MaixCAM / MaixCAM-Pro, the actual model file is `.cvimodel`, while the `.mud` file describes the model path, model type, preprocessing parameters, and label list. A common file pair is:

```text
yolov8n.mud
yolov8n_int8.cvimodel
```

Place the `.mud` and `.cvimodel` files in the same directory to avoid path mistakes.

## Prepare the ONNX Model

The goal of this section is to obtain a `.onnx` file that `tpu-mlir` can read. ONNX usually comes from one of these sources:

1. **Exported after training**: after training YOLOv8 / YOLO11 and obtaining a `.pt` file, follow [Train a YOLO Detection Model on a Computer](../vision/customize_model_yolo.md). MaixCAM commonly uses `320x224`; use a fixed input size instead of dynamic input shapes.
2. **Exported from another framework**: for example, PyTorch or TensorFlow. Make sure the exported ONNX has a fixed input shape and can be opened in Netron.
3. **Provided by a third party**: you can start from the ONNX file directly, but you need to confirm that the license allows usage and that the model structure is suitable for MaixCAM.

If `.mud` and `.cvimodel` files are already available, the model has already been converted for MaixCAM and can be deployed directly. This conversion flow is not required.

Place the ONNX file in a separate working directory and name it `model.onnx`. Then open it with [Netron](https://netron.app/) and record the following information:

| Item | Verification method | Subsequent use |
| --- | --- | --- |
| Input node name | Check the input node area in Netron; a common name is `images` | Input parameter for the ONNX extraction command |
| Input shape | Check the input node shape in Netron, for example `1x3x224x320` | `--input_shapes` parameter in `model_transform.py` |
| Candidate output nodes | Check the final output nodes before post-processing | Output parameters for the ONNX extraction command and `--output_names` in `model_transform.py` |

Also confirm that the model operators are supported by `tpu-mlir`. MaixCAM uses the `cv181x` processor. If conversion reports an unsupported operator, adjust the model structure during training/export, or use a model structure already supported by MaixPy.

## Find Suitable Quantization Output Nodes

The goal of this section is to generate `export.onnx`, which is used by the conversion command later.

Many detection models contain post-processing nodes at the end of the ONNX graph. These nodes are usually better handled by CPU code. Quantizing the full ONNX may increase quantization error or cause conversion failure, so first choose suitable output nodes and extract a smaller ONNX.

Use the following table to select output nodes for common model types. For YOLOv5, classification, and other models, see the [ONNX Node Trimming Tutorial](./onnx_export.md).

| Model type | Recommended output node choice | Next step |
| --- | --- | --- |
| YOLOv8 detection | For MaixCAM, use `/model.22/dfl/conv/Conv_output_0` and `/model.22/Sigmoid_output_0` | Copy the node names and extract ONNX |
| YOLO11 detection | For MaixCAM, use `/model.23/dfl/conv/Conv_output_0` and `/model.23/Sigmoid_output_0` | Copy the node names and extract ONNX |
| YOLOv5 detection | Commonly uses three detection head outputs, such as `/model.24/m.0/Conv_output_0`, `/model.24/m.1/Conv_output_0`, `/model.24/m.2/Conv_output_0` | Copy the node names and extract ONNX |
| pose / seg / obb models | These models have more output nodes | Confirm the nodes in the task-specific guide, then follow the trimming tutorial |
| Classification model | Use the final classification output; if the graph ends with `softmax`, use the output before `softmax` | Record that node name |

The node names in the table come from commonly used Ultralytics export versions. They are only navigation hints and cannot replace shape validation. Layer numbers may change between model versions, so use Netron to find nodes at equivalent positions and with equivalent semantics.

For the YOLOv8 Detect output scheme used in this page, the number of candidate boxes for an `H×W` input is:

```text
N = (H/8 × W/8) + (H/16 × W/16) + (H/32 × W/32)
```

For example, with a `320×224` input, `N = 1470`. For an 80-class model, the two outputs represent four bounding-box regression values and 80 class scores, so their shapes are `[1,4,1470]` and `[1,80,1470]`.

The 80 classification channels come from the 80 classes in the COCO reference model; for a custom model, this dimension must instead be its own class count `C`. The four regression values are the DFL-processed distances from each candidate location to the left, top, right, and bottom sides of its bounding box.

Do not proceed with conversion if the node names look similar but the shapes, number of outputs, or semantics do not match.

After confirming the input node name and output node names, install the tools needed for extraction and simplification:

```bash
pip install onnx onnxsim
```

For a YOLOv8 detection model, run:

```bash
python -c "import onnx,sys; onnx.utils.extract_model(sys.argv[1], sys.argv[2], [s.strip() for s in sys.argv[3].split(',')], [s.strip() for s in sys.argv[4].split(',')])" model.onnx tmp_extract.onnx "images" "/model.22/dfl/conv/Conv_output_0,/model.22/Sigmoid_output_0"
onnxsim tmp_extract.onnx export.onnx
```

Replace:

* `model.onnx` with your original ONNX file name.
* `"images"` with the input node name shown in Netron.
* `"/model.22/dfl/conv/Conv_output_0,...` with your selected output node names, separated by English commas.

After the command succeeds, `export.onnx` is generated in the current directory. All later `--model_def ./export.onnx` commands refer to this extracted and simplified ONNX file. For a more complete extraction explanation, see [ONNX Node Extraction Tutorial](./onnx_export.md).

## Install the Model Conversion Environment

MaixCAM model conversion uses Sophgo [tpu-mlir](https://github.com/sophgo/tpu-mlir). Use Docker to avoid host environment conflicts.

If Docker is not installed, follow [Docker's official documentation](https://docs.docker.com/engine/install/ubuntu/). After installation, run the following command. If it prints a version number, Docker is ready:

```shell
docker --version
```

Then pull the conversion image:

```shell
docker pull sophgo/tpuc_dev:latest
```

If pulling the image fails, download and load the image archive according to the official tpu-mlir instructions:

```shell
wget https://sophon-file.sophon.cn/sophon-prod-s3/drive/24/06/14/12/sophgo-tpuc_dev-v3.2_191a433358ad.tar.gz
docker load -i sophgo-tpuc_dev-v3.2_191a433358ad.tar.gz
```

Then check the actual image name:

```shell
docker images | grep tpuc
```

Enter your model conversion work directory and run the container:

```shell
mkdir -p ~/maixcam_convert
cd ~/maixcam_convert
docker run --privileged --rm -it -v "$PWD":/workspace -w /workspace sophgo/tpuc_dev:latest
```

If your image name is not `sophgo/tpuc_dev:latest`, replace it with the actual name shown by `docker images`. Inside the container, the current directory is `/workspace`. Put `export.onnx`, the test image, and calibration images in this directory for the following steps.

Install and check `tpu-mlir` inside the container:

```shell
pip install tpu_mlir
model_transform.py --help
```

If `model_transform.py --help` prints the help message, the environment is ready.

## Convert the ONNX Model to cvimodel

Before conversion, prepare these files in the working directory:

```text
.
├── export.onnx
├── test.jpg
└── images/
    ├── 0001.jpg
    ├── 0002.jpg
    └── ...
```

| File | How to prepare it | Purpose |
| --- | --- | --- |
| `export.onnx` | Generated by extracting and simplifying ONNX in the previous step | Input model for `model_transform.py` |
| `test.jpg` | Any test image that matches the model scenario | Used to compare ONNX and MLIR outputs during conversion |
| `images/` | 20 to 200 representative real-scene images | Calibration dataset for INT8 quantization |

Images closer to the actual deployment scene usually produce more stable INT8 results.

### Generate the MLIR Intermediate File

For a YOLOv8 detection model, run `model_transform.py` first:

```bash
model_transform.py \
--model_name yolov8n \
--model_def ./export.onnx \
--input_shapes [[1,3,224,320]] \
--mean "0,0,0" \
--scale "0.00392156862745098,0.00392156862745098,0.00392156862745098" \
--keep_aspect_ratio \
--pixel_format rgb \
--channel_format nchw \
--output_names "/model.22/dfl/conv/Conv_output_0,/model.22/Sigmoid_output_0" \
--test_input ./test.jpg \
--test_result yolov8n_top_outputs.npz \
--tolerance 0.99,0.99 \
--mlir yolov8n.mlir
```

After success, you will get `yolov8n.mlir`, `yolov8n_in_f32.npz`, and `yolov8n_top_outputs.npz`. The deploy command uses these files next.

Important parameters:

| Parameter | Value |
| --- | --- |
| `--model_name` | Model name used for generated intermediate files, such as `yolov8n` |
| `--model_def` | The extracted ONNX, for example `./export.onnx` |
| `--input_shapes` | Model input shape in `[N,C,H,W]`, for example `[[1,3,224,320]]` |
| `--mean` / `--scale` | Preprocessing parameters; keep them consistent with training and export |
| `--output_names` | ONNX output node names; must match the nodes used when extracting `export.onnx` |
| `--test_input` | Test image path, such as `./test.jpg` |
| `--test_result` | Output comparison result used by the next step |
| `--mlir` | Generated MLIR intermediate file |

### Generate an INT8 cvimodel

On MaixCAM, INT8 is usually preferred because it is faster and uses less memory. First generate the calibration table:

```bash
run_calibration.py yolov8n.mlir \
--dataset ./images \
--input_num 50 \
-o yolov8n_cali_table
```

`--input_num` is the number of images used for calibration and cannot be larger than the number of images in `images/`. Beginners can start with about 50 real-scene images.

Then generate the `.cvimodel`:

```bash
model_deploy.py \
--mlir yolov8n.mlir \
--quantize INT8 \
--quant_input \
--calibration_table yolov8n_cali_table \
--processor cv181x \
--test_input yolov8n_in_f32.npz \
--test_reference yolov8n_top_outputs.npz \
--tolerance 0.9,0.6 \
--model yolov8n_int8.cvimodel
```

After successful execution, `yolov8n_int8.cvimodel` is generated in the current directory.

If INT8 conversion fails, first check whether the output nodes, input shape, preprocessing parameters, and calibration images are correct. If it still cannot pass, try BF16:

```bash
model_deploy.py \
--mlir yolov8n.mlir \
--quantize BF16 \
--processor cv181x \
--test_input yolov8n_in_f32.npz \
--test_reference yolov8n_top_outputs.npz \
--model yolov8n_bf16.cvimodel
```

BF16 usually preserves accuracy more easily, but it is often slower and uses more memory than INT8. Use it mainly for debugging or special accuracy requirements.

## Write the `mud` File

The `.mud` and `.cvimodel` files must be in the same directory. For `yolov8n_int8.cvimodel`, create `yolov8n.mud`:

```ini
[basic]
type = cvimodel
model = yolov8n_int8.cvimodel

[extra]
model_type = yolov8
input_type = rgb
mean = 0, 0, 0
scale = 0.00392156862745098, 0.00392156862745098, 0.00392156862745098
labels = person, bicycle, car, motorcycle, airplane, bus, train, truck, boat, traffic light, fire hydrant, stop sign, parking meter, bench, bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe, backpack, umbrella, handbag, tie, suitcase, frisbee, skis, snowboard, sports ball, kite, baseball bat, baseball glove, skateboard, surfboard, tennis racket, bottle, wine glass, cup, fork, knife, spoon, bowl, banana, apple, sandwich, orange, broccoli, carrot, hot dog, pizza, donut, cake, chair, couch, potted plant, bed, dining table, toilet, tv, laptop, mouse, remote, keyboard, cell phone, microwave, oven, toaster, sink, refrigerator, book, clock, vase, scissors, teddy bear, hair drier, toothbrush
```

Modify these fields for your own model:

| Parameter | Description |
| --- | --- |
| `model` | The `.cvimodel` file name, such as `yolov8n_int8.cvimodel` |
| `model_type` | Model type supported by MaixPy, such as `yolov5`, `yolov8`, `yolo11`, or `classifier` |
| `mean` / `scale` | Preprocessing parameters; keep them consistent with training, export, and conversion |
| `labels` | Class names; the count and order must match the training dataset exactly |

For example, if you trained a digit detector with classes `0` to `9`, write:

```ini
labels = 0,1,2,3,4,5,6,7,8,9
```

## Deploy to the Device and Verify Quickly

MaixPy usually loads the `.mud` file. The `.mud` file then points to the actual `.cvimodel` file. The simplest approach is to put both files in the same directory:

```text
/root/models/yolov8n.mud
/root/models/yolov8n_int8.cvimodel
```

Then first confirm that the model can be loaded:

```python
from maix import nn

model = nn.NN("/root/models/yolov8n.mud")
print(model)
```

If the model type is already supported by MaixPy, prefer the wrapped API. For example, for YOLO, see the [YOLO object detection documentation](../vision/yolov5.md):

```python
from maix import nn

detector = nn.YOLOv8(model="/root/models/yolov8n.mud", dual_buff=True)
```

## Debug Checklist

If the model cannot be loaded or the result is wrong, check these items first:

1. Whether the `.mud` and `.cvimodel` files are in the same directory, and whether `model` in the `.mud` file uses the correct file name.
2. Whether the path used on the device really exists, such as `/root/models/yolov8n.mud`.
3. Whether `labels` exactly matches the class count and class order used during training.
4. Whether `model_type` is supported by MaixPy, such as `yolov5`, `yolov8`, `yolo11`, or `classifier`.
5. Whether input resolution, `mean`, `scale`, and RGB/BGR order match training, export, and conversion settings.
6. Whether ONNX output nodes, the extraction command, and `--output_names` in `model_transform.py` are exactly the same.
7. If you are not sure whether the problem is the model or your code, test with a MaixHub model or a built-in model first. After an official model runs correctly, debug your own model.

When asking for help, provide the ONNX export command, model task and class count, input and output names and shapes, complete conversion command, tool versions, MUD file, MaixPy / system version, and complete error log.

After these basic checks pass, continue with the specific model documentation or conversion workflow.

## Write Post-processing Code

If the model type is already supported by MaixPy, such as YOLO or a classifier, you usually do not need to write post-processing manually. Use the corresponding MaixPy API directly.

If MaixPy does not yet wrap your model type, implement post-processing according to the model outputs:

* **Quick verification**: use `maix.nn.NN` to load the `.mud` file, call `forward` or `forward_image`, and write post-processing in Python. See [Porting a New Model](../pro/customize_model.md) for the full workflow.
* **Formal integration**: add a model decoding class in `MaixCDK` so both `MaixCDK` and `MaixPy` can use it with better performance. You can refer to the [YOLOv5 source code](https://github.com/sipeed/MaixCDK/blob/71d5b3980788e6b35514434bd84cd6eeee80d085/components/nn/include/maix_nn_yolov5.hpp), add the corresponding `hpp` file, complete the `@maixpy` annotations, and rebuild MaixPy.

After adding support for a new model, you can submit a Pull Request to the main `MaixPy` repository or share your model on [MaixHub](https://maixhub.com/share).
