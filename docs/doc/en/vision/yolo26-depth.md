---
title: MaixCAM2 MaixPy Monocular Depth Estimation with YOLO26-depth
update:
  - date: 2026-08-08
    version: v1.0
    author: Tao
    content: Add YOLO26-depth code and documentation support
---

## Introduction

YOLO26-depth is a monocular depth estimation model released by Ultralytics. It predicts a per-pixel depth map from a single RGB image, where each pixel outputs an estimated distance in meters. Compared with Depth-Anything-V2, YOLO26-depth runs inference faster at the same resolution (YOLO26n-depth is about 7.7x faster than Depth-Anything V2 Small on T4 TensorRT fp16), making it suitable for real-time depth estimation scenarios. For details, see the official open-source repository or the Ultralytics depth estimation documentation.

The model uses a log-depth head, outputs unbounded depth (about 0.02~150m), and has built-in cross-domain calibration parameters (`cal_a`/`cal_b`) that map relative depth to absolute meters.

## Supported Devices

| Device | Supported |
| --- | --- |
| MaixCAM2 | ✅ |
| MaixCAM | ❌ |

## Using YOLO26-depth on MaixCAM2 MaixPy

After putting the model files on the device, run the code directly:

```python
from maix import app, camera, display, image, nn

cmap = image.CMap.JET
# Optional calibration parameters: d_real = exp(cal_a * log(d_raw) + cal_b), no calibration by default (1.0, 0.0)
CAL_A, CAL_B = 1.0,0.0
model = nn.YOLO26Depth(model="/root/models/yolo26n_depth_640x480.mud", dual_buff=True)

cam = camera.Camera(model.input_width(), model.input_height(), model.input_format())
disp = display.Display()

while not app.need_exit():
    img = cam.read()
    res = model.get_depth_image(img, image.Fit.FIT_CONTAIN, cmap, CAL_A, CAL_B)
    if res:
        disp.show(res)
```

Here `get_depth_image` directly returns a pseudo-color depth heatmap. `cmap` can be set to a colormap; all supported pseudo-colors can be found in the `maix.image.CMap` API documentation. Default is JET (red/yellow near, blue far, high contrast).

If you want the raw model output (float32 depth data in meters), you can also use the `get_depth` method:

```python
depth = model.get_depth(img, image.Fit.FIT_CONTAIN, CAL_A, CAL_B)
# Convert to numpy for use
import maix.tensor as mt
depth_np = mt.tensor_to_numpy_float32(depth).reshape(model.output_height(), model.output_width())
```

## Reading Distance at a Specified Position

`get_distance` can directly read the estimated distance (in meters) at a coordinate in the image, without parsing the depth tensor yourself:

```python
dist = model.get_distance(depth, x, y, img.width(), img.height(), image.Fit.FIT_CONTAIN)
print(f"distance at ({x},{y}): {dist:.2f} m")
```

## Notes

### Depth Scale Calibration

YOLO26-depth outputs relative log depth; absolute meters depend on the global calibration parameters built into the model. This global calibration is fitted on a "indoor + outdoor mixed domain" and may be inaccurate for a specific camera or close-range scenes (<1m):

- Close range (tens of centimeters) may be displayed magnified as 1m+, and near-end measurement accuracy is limited
- If you need to recover absolute meters for a specific camera/scene, you can collect several known-distance points, fit `d_real = exp(a * log(d_raw) + b)` to get `a` and `b`, and pass them when calling `get_depth`/`get_depth_image`

### How to Calibrate (Automatic Collection Script)

Calibration essence: collect paired data of "real distance vs model output" and fit two parameters with log-log linear regression:

```
log(d_real) = a * log(d_raw) + b      =>   d_real = exp(a * log(d_raw) + b)
```

An automatic collection script is provided below. Run it on the device; it automatically outputs the distance predicted at the center point, collects points one by one via the touchscreen, automatically fits, and outputs `cal_a` and `cal_b`.

**① Script content**:

```python
"""YOLO26-depth automatic collection + calibration fitting script
Usage:
  The screen shows the target distance and real-time center depth; place the object at the target distance and tap the screen to record
  After collecting all distances, automatically fit: d_real = exp(a * log(d_raw) + b)
"""

import math
import numpy as np
from maix import app, camera, display, image, nn, touchscreen, time

MODEL = "/root/models/yolo26n_depth_640x480.mud"
DISTANCES_M = [0.15, 0.25, 0.40, 0.60, 0.80, 1.00, 1.50, 2.00]
FRAMES_PER_SAMPLE = 10
SETTLE_FRAMES = 5
OUT_FILE = "/root/calib_data.txt"


def main():
    model = nn.YOLO26Depth(MODEL, dual_buff=False)
    cam = camera.Camera(model.input_width(), model.input_height(), model.input_format())
    disp = display.Display()
    touch = touchscreen.TouchScreen()
    cam_w, cam_h = cam.width(), cam.height()
    cx, cy = cam_w // 2, cam_h // 2
    print(f"model {model.input_width()}x{model.input_height()}, camera {cam_w}x{cam_h}")

    def center_dist(img):
        """Return the center distance in meters, or NaN if invalid."""
        d = model.get_depth(img, image.Fit.FIT_CONTAIN)
        if d is None:
            return float("nan")
        v = model.get_distance(d, cx, cy, cam_w, cam_h, image.Fit.FIT_CONTAIN)
        del d
        return v

    for _ in range(10):                      # warmup
        img = cam.read()
        if img is not None:
            center_dist(img)

    samples, idx, was_pressed = [], 0, False
    print(f"start collecting {len(DISTANCES_M)} distances: {DISTANCES_M}, place the object and tap the screen")

    while idx < len(DISTANCES_M) and not app.need_exit():
        d_real = DISTANCES_M[idx]
        img = cam.read()
        if img is None:
            continue
        d_raw = center_dist(img)

        show = img.copy()
        show.draw_string(10, 10, f"Target: {d_real:.2f} m ({idx+1}/{len(DISTANCES_M)})", image.COLOR_WHITE)
        show.draw_string(10, 40, f"Center depth: {d_raw:.3f} m", image.COLOR_WHITE)
        show.draw_string(10, 70, "Place object, tap to record", image.COLOR_WHITE)
        show.draw_circle(cx, cy, 6, image.COLOR_RED, -1)
        disp.show(show)
        del show

        try:
            pressed = bool(touch.read()[2])
        except Exception:
            pressed = False
        if was_pressed and not pressed:
            vals = []
            for _ in range(SETTLE_FRAMES):
                cam.read()
            for _ in range(FRAMES_PER_SAMPLE):
                f = cam.read()
                if f is None:
                    continue
                v = center_dist(f)
                if not math.isnan(v):
                    vals.append(v)
            if vals:
                samples.append((d_real, float(np.mean(vals))))
                print(f"[{len(samples)}/{len(DISTANCES_M)}] real={d_real:.3f}m model={np.mean(vals):.3f}m")
                idx += 1
        was_pressed = pressed
        time.sleep_ms(10)

    print("\n===== collection done =====")
    if len(samples) < 3:
        print("fewer than 3 valid samples, cannot fit")
        return

    d_real = np.array([s[0] for s in samples])
    d_raw = np.array([s[1] for s in samples])
    a, b = np.polyfit(np.log(d_raw), np.log(d_real), 1)
    for r, w, c in zip(d_real, d_raw, np.exp(a * np.log(d_raw) + b)):
        print(f"  real={r:.3f}m model={w:.3f}m calibrated={c:.3f}m error={abs(c-r)/r*100:.1f}%")
    print(f"\n>>> cal_a = {a:.6f}\n>>> cal_b = {b:.6f}")
    with open(OUT_FILE, "w") as f:
        f.write(f"cal_a = {a:.6f}\ncal_b = {b:.6f}\n")
        for r, w in samples:
            f.write(f"{r:.3f} {w:.3f}\n")
    print(f"data saved to {OUT_FILE}")


if __name__ == "__main__":
    main()
```

**② Calibration steps**:

1. Run the script in MaixVision
2. Modify the distance list `DISTANCES_M` at the top of the script as needed (cover your usage range, collect more groups):
   ```python
   DISTANCES_M = [0.15, 0.25, 0.40, 0.60, 0.80, 1.00, 1.50, 2.00]
   ```
3. The screen shows `Target: 0.15 m (1/8)` and the real-time `Center depth`:
   - Take a textured object (palm/cardboard box/phone), place it at exactly 0.15m in front of the lens (measure from the lens plane to the object surface with a tape measure)
   - Tap the screen -> automatically collect 10 frames and average -> move to the next group
   - Repeat until all distances are collected
4. The script automatically fits and outputs:
   ```
   >>> cal_a = 0.850000
   >>> cal_b = 0.400000
   data saved to /root/calib_data.txt
   ```

**③ Apply the calibration parameters**:

Pass the output `cal_a`/`cal_b` to the inference API:

```python
CAL_A, CAL_B = 1.0, 0.0    # replace with the fitting result
res = model.get_depth_image(img, image.Fit.FIT_CONTAIN, cmap, CAL_A, CAL_B)
# or read the raw depth:
depth = model.get_depth(img, image.Fit.FIT_CONTAIN, CAL_A, CAL_B)
```

**Notes**:
- The object should be as large as possible and cover the center of the image (the script uses the center pixel)
- Measure the real distance from the **lens plane**, not the device body
- Calibration only corrects overall scale offset; it cannot recover the resolution lost by model quantization
- Re-calibrate after changing the camera or mounting angle (`a`/`b` are strongly camera-dependent)

### Output Is a Relative Value

Similar to Depth-Anything, if no calibration is applied, the absolute value of the model output varies with the image content (e.g., the value range is larger when the scene depth span is large), and the depth will flicker slightly between consecutive video frames.

### Converting to Different Resolutions
The default resolution is 680*480. If you want to use another resolution, you can convert the model yourself as follows:

**①Download the original pt model:**

Visit the [Yolo26-Depth official website](https://docs.ultralytics.com/zh/tasks/depth) to download models of different precision (default 768*768)

**②Export the onnx model at the desired resolution:**

A one-click export script is provided here to export an ONNX model at the desired resolution:
```python
"""YOLO26-depth.pt -> ONNX at any size.
    # YOLO26 depth models require ultralytics>=8.4.49

Usage:
    python export_to_onnx.py yolo26n-depth.pt --imgsz 640          # fixed 640x640
    python export_to_onnx.py yolo26s-depth.pt --imgsz 640x480      # any widthxheight (stride-aligned automatically)
    python export_to_onnx.py yolo26n-depth.pt --imgsz 640 --dynamic  # dynamic size
"""
import argparse
from ultralytics import YOLO

a = argparse.ArgumentParser(description="Export ONNX at any size")
a.add_argument("model", nargs="?", default="yolo26n-depth.pt")
a.add_argument("--imgsz", default="768", help="any size: 768 or 640x480 (widthxheight)")
a.add_argument("--dynamic", action="store_true", help="export dynamic size (H/W/batch not fixed)")
a.add_argument("--batch", type=int, default=1)
args = a.parse_args()

imgsz = args.imgsz
if "x" in imgsz:
    w, h = imgsz.lower().split("x")
    imgsz = (int(h), int(w))  # ultralytics uses (H, W)
else:
    imgsz = int(imgsz)
```
**③Write the conversion config:**
```json
{
  "input": "./yolo26n_depth_640x480.onnx",
  "output_dir": "./output",
  "output_name": "yolo26n_depth_640x480.axmodel",
  "model_type": "ONNX",
  "target_hardware": "AX620E",
  "npu_mode": "NPU2",
  "onnx_opt": {
    "disable_onnx_optimization": false,
    "enable_onnxsim": true
  },
  "quant": {
    "input_configs": [
      {
        "tensor_name": "images",
        "calibration_dataset": "./calib_data.zip",
        "calibration_size": -1,
        "calibration_mean": [0, 0, 0],
        "calibration_std": [255, 255, 255]
      }
    ],
    "layer_configs": [
      {
        "start_tensor_names": ["DEFAULT"],
        "end_tensor_names": ["DEFAULT"],
        "data_type": "U8"
      }
    ],
    "calibration_method": "MinMax",
    "precision_analysis": true,
    "precision_analysis_method": "EndToEnd",
    "precision_analysis_mode": "Reference"
  },
  "input_processors": [
    {
      "tensor_name": "images",
      "tensor_layout": "NCHW",
      "src_dtype": "U8",
      "src_layout": "NHWC"
    }
  ],
  "compiler": {
    "check": 0
  }
}
```
**Notes**:
1. The quantization dataset calib_data.zip can contain a few COCO dataset images
2. You can set `npu_mode` to `NPU1` and add the `vnpu` suffix to output_name — that means it's using the VNPU. The model will be a bit slower, but you can turn on `AI-ISP` in settings to get better camera quality.
3. You can also set `npu_mode` to `NPU2` and add the `npu` suffix to output_name — that means it's using the full NPU. This gives you the fastest model speed, but you have to turn off `AI-ISP` in settings for it to work.

**④Start conversion:**

Run the command in the pulsar2 container to start model conversion:
```bash
pulsar2 build --config config.json
```

⑤Write the MUD file:
```mud
[basic]
type = axmodel
model_npu = yolo26n_depth_640x480_npu.axmodel
model_vnpu = yolo26n_depth_640x480_vnpu.axmodel

[extra]
model_type = yolo26_depth
input_type = rgb

input_cache = true
output_cache = true
input_cache_flush = false
output_cache_inval = true
```
