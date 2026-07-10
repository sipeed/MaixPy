---
title: Graphical Model Conversion Platform
---

## Introduction

After reading the previous model-conversion guides, have all those commands started to blur together? Exporting ONNX, locating output nodes, trimming the model, preparing calibration images, editing configuration files, and running Docker commands—missing a single parameter can send you back through the whole process. Sometimes converting a trained `.pt` model feels harder than training it in the first place.

Do not worry, and put away that command-line checklist. Maix Converter Platform brings the complicated steps together in a Web interface. Upload the model and calibration dataset, select the target device, YOLO version, and input resolution, and the platform will handle model export, node processing, quantization, MUD generation, and result packaging automatically.

There is no need to memorize long commands or repeatedly enter Docker containers. A few clicks and a little patience are enough to produce a YOLO Detect model for MaixCAM, MaixCAM Pro, or MaixCAM2.

## Current Support

The platform currently supports the following devices and models:

| Item | Supported |
| --- | --- |
| Target devices | MaixCAM, MaixCAM Pro, MaixCAM2 |
| Model types | YOLO26, YOLO11, YOLOv8 |
| Tasks | Object detection (Detect) |
| Input models | `.pt`, `.onnx` |
| Calibration dataset | A `.zip` file containing images |

> Classification, segmentation, pose estimation, and OBB tasks are not currently supported. For other models or custom conversion parameters, use the manual conversion methods described in the previous guides.

## Get the Conversion Platform

Maix Converter Platform is open source. Its source code is available at [github.com/sipeed/maix_converter_platform](https://github.com/sipeed/maix_converter_platform).

Clone the repository with Git:

```shell
git clone https://github.com/sipeed/maix_converter_platform.git
cd maix_converter_platform
```

## Prepare the Python Environment

Using Conda to create an independent Python 3.11 environment is recommended to avoid conflicts with existing packages:

```shell
conda create -n maix-converter python=3.11 -y
conda activate maix-converter
pip install -r requirements-web.txt
```

To upload a `.pt` model and let the platform export it to ONNX automatically, also install Ultralytics and ONNX:

```shell
pip install ultralytics onnx
```

If you only upload an existing `.onnx` model, `ultralytics` is not required. Installing `onnx` is still recommended for custom-trained models because the platform can try to read class names from the model metadata and write them to the MUD file.

## Prepare the Docker Environment

The model-conversion toolchains run inside Docker. Install Docker first and verify that the current user can run it:

```shell
docker --version
docker ps
```

If `docker ps` completes without a permission error, Docker is ready.

> Different devices use different conversion toolchains. If you only convert models for one device family, you only need to prepare its corresponding Docker image.

### MaixCAM2 Conversion Image

MaixCAM2 uses the Pulsar2 toolchain. The platform expects the image name `pulsar2:6.0`. For download and import instructions, see [Convert an ONNX model for MaixCAM2](./maixcam2.md).

After downloading the image archive, import it and inspect the image name:

```shell
docker load -i pulsar2_vxx.tar.gz
docker images
```

If the imported image is not named `pulsar2:6.0`, add the expected tag using its actual name. For example:

```shell
docker tag pulsar2:3.3 pulsar2:6.0
```

Finally, verify that Pulsar2 works:

```shell
docker run --rm pulsar2:6.0 -c "pulsar2 version"
```

### MaixCAM / MaixCAM Pro Conversion Image

MaixCAM and MaixCAM Pro use the TPU-MLIR toolchain. The platform ultimately uses an image named `maixcam-tpumlir:v3.4`. First obtain the `sophgo/tpuc_dev` base image. For download instructions, see [Convert an ONNX model for MaixCAM](./maixcam.md).

After downloading the image archive, import it and check its actual name:

```shell
docker load -i tpuc_dev_vxx.tar.gz
docker images
```

The Dockerfile provided by the conversion platform uses `sophgo/tpuc_dev:v3.4` by default. If the imported image already has this name, no changes are needed. Otherwise, add the expected tag based on the name shown by `docker images`. For example, if the imported image is `sophgo/tpuc_dev:latest`, run:

```shell
docker tag sophgo/tpuc_dev:latest sophgo/tpuc_dev:v3.4
```

After confirming the base-image name, build the image used by the platform from the repository root:

```shell
docker build -f docker/maixcam-tpumlir.Dockerfile -t maixcam-tpumlir:v3.4 .
```

Inspect the result and verify the conversion command:

```shell
docker images
docker run --rm maixcam-tpumlir:v3.4 model_transform.py --help
```

If the help text for `model_transform.py` appears, the conversion environment is ready.

## Start the Conversion Platform

Enter the repository root and activate the Conda environment created earlier:

```shell
cd maix_converter_platform
conda activate maix-converter
```

Start the Web service:

```shell
uvicorn web.app:app --host 0.0.0.0 --port 8000
```

Open the following address in a browser:

```text
http://127.0.0.1:8000
```

When accessing the conversion server from another computer, replace `127.0.0.1` with the server's IP address.

## Prepare the Model and Calibration Dataset

The platform accepts `.pt` and `.onnx` model files:

- When uploading `.pt`, the platform uses the width and height entered on the page to export an ONNX model with the corresponding input resolution through Ultralytics.
- When uploading `.onnx`, the platform proceeds directly to model processing and conversion and uses the model's own static input shape. The width and height entered on the page do not resize the model, so using values that match the actual ONNX input resolution is recommended.

The calibration dataset must be packaged as a `.zip` file containing images only; annotation files are not required. Supported image formats are `.jpg`, `.jpeg`, `.png`, and `.bmp`.

Images may be stored directly in the archive:

```text
dataset.zip
  000001.jpg
  000002.jpg
  000003.jpg
```

The archive may also contain nested directories:

```text
dataset.zip
  images/
    000001.jpg
    000002.jpg
```

Calibration images should resemble the model's actual deployment environment. For example, if the model will process camera images, prefer images captured by a similar camera under realistic conditions. Start with 50–100 images for a quick test and increase the number as appropriate for the final conversion.

## Create a Conversion Job

Open the Web page and complete the form from top to bottom:

| Option | Description |
| --- | --- |
| Model file | Upload the `.pt` or `.onnx` model to convert |
| Calibration dataset | Upload a `.zip` file containing calibration images only |
| Model name | Base name for generated files, such as `yolo11n` |
| Target device | Select MaixCAM2 or MaixCAM / Pro for the actual device |
| YOLO version | Must match the version of the uploaded model |
| Image count | Number of calibration images; it cannot exceed the number of valid images in the archive |
| Width and height | Set the exported model input resolution for `.pt` uploads. For `.onnx` uploads, the model's own static input shape is used. The platform requires both entered values to be between 32 and 4096 and multiples of 32 |
| Fast mode | Skips some checks to shorten conversion time and is useful for testing the workflow |

Click **Start Conversion** after completing the form. The page displays upload progress, the current job status, and live conversion logs. Conversion time depends on the model size, calibration image count, and computer performance.

> Fast mode is useful for checking the environment and workflow. Before deployment, disable fast mode and perform a complete conversion again.

## Download the Conversion Result

After a successful conversion, the **Download Result** button becomes available. Click it to download a ZIP archive containing the generated model files.

A MaixCAM2 result normally contains:

```text
model_name.mud
model_name_npu.axmodel
model_name_vnpu.axmodel
```

A MaixCAM or MaixCAM Pro result normally contains:

```text
model_name.mud
model_name.cvimodel
```

Extract the archive and copy all model files to the same directory on the device. The MaixPy program only needs to load the `.mud` file, which references the actual model files in the same directory.

The following example uses YOLO11:

```python
from maix import app, camera, display, image, nn

detector = nn.YOLO11(model="/root/models/yolo11n.mud", dual_buff=True)
cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
disp = display.Display()

while not app.need_exit():
    img = cam.read()
    objs = detector.detect(img, conf_th=0.5, iou_th=0.45)
    for obj in objs:
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color=image.COLOR_RED)
        msg = f"{detector.labels[obj.class_id]}: {obj.score:.2f}"
        img.draw_string(obj.x, obj.y, msg, color=image.COLOR_RED)
    disp.show(img)
```

For YOLO26 or YOLOv8, replace `nn.YOLO11` with the corresponding MaixPy model interface.

## View Jobs and Logs

Each conversion creates an independent job directory under `jobs/`:

```text
jobs/<job_id>/
```

The Web page lists recent jobs and provides their status, logs, result downloads, and deletion controls. If a conversion fails, check the live log first or inspect these files in the job directory:

```text
api.log
convert.log
job.json
```

`convert.log` contains the main output from the model-conversion toolchain and is usually the best place to diagnose output-node, calibration-dataset, Docker-image, or conversion-parameter problems.

## FAQ

### Docker Permission Denied

If `docker ps` reports insufficient permissions, Linux users can add the current user to the Docker group:

```shell
sudo usermod -aG docker $USER
```

Log out and back in after running the command, then check `docker ps` again.

### Docker Image Not Found

If the log contains `Unable to find image`, inspect the available image names:

```shell
docker images
```

MaixCAM2 requires `pulsar2:6.0`, while MaixCAM and MaixCAM Pro require `maixcam-tpumlir:v3.4`. A different repository name or tag prevents the platform from locating the conversion environment.

### Not Enough Calibration Images

The **Image Count** value cannot exceed the number of valid images in the uploaded ZIP archive. If the archive contains only 50 images, do not set the value to 100.

### Incorrect Classes in a Custom Model

The platform tries to read class names from the `.pt` model or ONNX metadata. If the deployed model reports incorrect class names or counts, check whether `labels` in the generated `.mud` file matches the trained model.

### Directory Mount Failure on Windows

Windows users must ensure that Docker Desktop is running with the WSL2 backend enabled. Keep the project in a short path containing only ASCII characters, such as `C:\maix_converter_platform`, to avoid Docker bind-mount problems caused by non-ASCII characters, special symbols, or deeply nested paths.

## Source Code

To report a problem, suggest an improvement, or request support for additional models, open an Issue in the project repository:

[github.com/sipeed/maix_converter_platform](https://github.com/sipeed/maix_converter_platform)
