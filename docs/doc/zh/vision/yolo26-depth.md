---
title: MaixCAM2 MaixPy 使用 YOLO26-depth 单目估计深度距离
update:
  - date: 2026-08-08
    version: v1.0
    author: Tao
    content: 增加 YOLO26-depth 代码和文档支持
---

## 简介

YOLO26-depth 是 Ultralytics 推出的单目深度估计模型，可以从单张 RGB 图像预测逐像素深度图，每个像素输出以米为单位的估计距离。与 Depth-Anything-V2 相比，YOLO26-depth 在同样的分辨率下推理速度更快（YOLO26n-depth 在 T4 TensorRT fp16 下比 Depth-Anything V2 Small 快约 7.7 倍），适合需要实时深度估计的场景。具体介绍可以看官方开源仓库或者 Ultralytics 深度估计文档。

模型采用 log-depth 头，输出无界深度（约 0.02~150m），并内置了跨域校准参数（`cal_a`/`cal_b`）将相对深度映射为绝对米数。

## 支持的设备

| 设备 | 是否支持 |
| --- | --- |
| MaixCAM2 | ✅ |
| MaixCAM | ❌ |

## 在 MaixCAM2 MaixPy 上使用 YOLO26-depth

将模型文件放到设备上后，直接运行代码即可：

```python
from maix import app, camera, display, image, nn

cmap = image.CMap.JET
# 可选校准参数: d_real = exp(cal_a * log(d_raw) + cal_b), 默认不校准(1.0, 0.0)
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

这里通过 `get_depth_image` 直接获得一张伪彩色深度热力图，`cmap` 可以指定为彩色，支持的所有伪彩色可以看 `maix.image.CMap` API 文档，默认 JET（近处红/黄、远处蓝，对比鲜明）。

如果你想要模型原始输出（float32 深度数据，单位米），也可以用 `get_depth` 方法：

```python
depth = model.get_depth(img, image.Fit.FIT_CONTAIN, CAL_A, CAL_B)
# 转换为 numpy 使用
import maix.tensor as mt
depth_np = mt.tensor_to_numpy_float32(depth).reshape(model.output_height(), model.output_width())
```

## 在指定位置读取距离

`get_distance` 可以直接读取画面中某个坐标的估计距离（米），不需要自己解析深度张量：

```python
dist = model.get_distance(depth, x, y, img.width(), img.height(), image.Fit.FIT_CONTAIN)
print(f"({x},{y}) 处距离: {dist:.2f} m")
```

## 注意点

### 深度尺度校准

YOLO26-depth 输出的是相对对数深度，绝对米数依赖模型内置的全局校准参数。该全局校准按"室内+室外混合域"拟合，对特定摄像头或近距离场景（<1m）可能不准：

- 近距离（十几厘米）可能被放大显示为 1m+，且端测量精度受限
- 若需要恢复特定摄像头/场景的绝对米数，可以采集若干已知距离点，拟合 `d_real = exp(a * log(d_raw) + b)` 得到 `a`、`b`，在调用 `get_depth`/`get_depth_image` 时传入即可

### 如何校准（自动采集脚本）

校准本质：采集"真实距离 vs 模型输出"的配对数据，用 log-log 线性回归拟合两个参数：

```
log(d_real) = a * log(d_raw) + b      =>   d_real = exp(a * log(d_raw) + b)
```

下面提供自动采集脚本,在设备上运行,自动输出中心点预测的距离,通过触摸屏逐点采集,自动拟合并输出 `cal_a`、`cal_b`。

**① 脚本内容**：

```python
"""YOLO26-depth 自动采集 + 校准拟合脚本
操作:
  屏幕显示目标距离与实时中心深度, 物体放到目标距离后点击屏幕记录
  采完所有距离后自动拟合: d_real = exp(a * log(d_raw) + b)
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
        """返回画面中心距离(米), 无效返回 NaN。"""
        d = model.get_depth(img, image.Fit.FIT_CONTAIN)
        if d is None:
            return float("nan")
        v = model.get_distance(d, cx, cy, cam_w, cam_h, image.Fit.FIT_CONTAIN)
        del d
        return v

    for _ in range(10):                      # 预热
        img = cam.read()
        if img is not None:
            center_dist(img)

    samples, idx, was_pressed = [], 0, False
    print(f"开始采集 {len(DISTANCES_M)} 个距离: {DISTANCES_M}, 放好物体后点击屏幕")

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
                print(f"[{len(samples)}/{len(DISTANCES_M)}] 真实={d_real:.3f}m 模型={np.mean(vals):.3f}m")
                idx += 1
        was_pressed = pressed
        time.sleep_ms(10)

    print("\n===== 采集完成 =====")
    if len(samples) < 3:
        print("有效样本不足 3 组, 无法拟合")
        return

    d_real = np.array([s[0] for s in samples])
    d_raw = np.array([s[1] for s in samples])
    a, b = np.polyfit(np.log(d_raw), np.log(d_real), 1)
    for r, w, c in zip(d_real, d_raw, np.exp(a * np.log(d_raw) + b)):
        print(f"  真实={r:.3f}m 模型={w:.3f}m 校准后={c:.3f}m 误差={abs(c-r)/r*100:.1f}%")
    print(f"\n>>> cal_a = {a:.6f}\n>>> cal_b = {b:.6f}")
    with open(OUT_FILE, "w") as f:
        f.write(f"cal_a = {a:.6f}\ncal_b = {b:.6f}\n")
        for r, w in samples:
            f.write(f"{r:.3f} {w:.3f}\n")
    print(f"数据已保存到 {OUT_FILE}")


if __name__ == "__main__":
    main()
```

**② 校准步骤**：

1. 在Maixvision运行脚本
2. 按需修改脚本顶部的距离列表 `DISTANCES_M`（覆盖你的使用范围，多采几组）：
   ```python
   DISTANCES_M = [0.15, 0.25, 0.40, 0.60, 0.80, 1.00, 1.50, 2.00]
   ```
3. 屏幕显示 `Target: 0.15 m (1/8)` 与实时 `Center depth`：
   - 拿一个有纹理的物体（手掌/纸盒/手机），放在镜头前正好 0.15m 处（用卷尺从镜头平面量到物体表面）
   - 点击屏幕 → 自动采集 10 帧取平均 → 进入下一组
   - 重复直到采完全部距离
4. 脚本自动拟合并输出：
   ```
   >>> cal_a = 0.850000
   >>> cal_b = 0.400000
   数据已保存到 /root/calib_data.txt
   ```

**③ 应用校准参数**：

把输出的 `cal_a`/`cal_b` 传入推理 API 即可：

```python
CAL_A, CAL_B = 1.0, 0.0    # 替换成拟合结果
res = model.get_depth_image(img, image.Fit.FIT_CONTAIN, cmap, CAL_A, CAL_B)
# 或读取原始深度:
depth = model.get_depth(img, image.Fit.FIT_CONTAIN, CAL_A, CAL_B)
```

**注意事项**：
- 物体尽量大、覆盖画面中心（脚本取的是中心像素）
- 真实距离从**镜头平面**量起，不是机身
- 校准只能修正整体尺度偏移，无法恢复模型量化丢掉的分辨率
- 换摄像头/换安装角度后需重新校准（`a`、`b` 与摄像头强相关）

### 输出为相对值

和 Depth-Anything 类似，若不做校准，模型输出的绝对值会随图像内容变化（比如场景深度范围大时数值跨度大），连续视频帧间深度会有轻微闪动。

### 转换不同分辨率
默认采用的分辨率为 680*480, 如果你期望使用其它分辨率，可以按照以下方法自行转换:

**①下载原始pt模型:**

访问[Yolo26-Depth官网](https://docs.ultralytics.com/zh/tasks/depth)下载不同精度的模型(默认768*768)

**②导出所需分辨率的onnx模型:**

这里提供一键导出脚本,用于导出所需的分辨率的onnx模型:
```python
"""YOLO26-depth.pt -> 任意尺寸 ONNX。
    # YOLO26 depth 模型需要 ultralytics>=8.4.49

用法:
    python export_to_onnx.py yolo26n-depth.pt --imgsz 640          # 固定 640x640
    python export_to_onnx.py yolo26s-depth.pt --imgsz 640x480      # 任意宽x高(自动对齐 stride)
    python export_to_onnx.py yolo26n-depth.pt --imgsz 640 --dynamic  # 动态尺寸
"""
import argparse
from ultralytics import YOLO

a = argparse.ArgumentParser(description="导出任意尺寸 ONNX")
a.add_argument("model", nargs="?", default="yolo26n-depth.pt")
a.add_argument("--imgsz", default="768", help="任意尺寸: 768 或 640x480(宽x高)")
a.add_argument("--dynamic", action="store_true", help="导出动态尺寸(H/W/batch 不固定)")
a.add_argument("--batch", type=int, default=1)
args = a.parse_args()

imgsz = args.imgsz
if "x" in imgsz:
    w, h = imgsz.lower().split("x")
    imgsz = (int(h), int(w))  # ultralytics 用 (H, W)
else:
    imgsz = int(imgsz)
```
**③编写转换配置:**
```json
{
  "input": "./yolo26n_depth_640x480.onnx",
  "output_dir": "./output",
  "output_name": "yolo26n_depth_640x480_npu.axmodel",
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
**注意事项**:
1. 量化数据集`calib_data.zip`可以放几张COCO数据集
2. `npu_mode`可以设置为`NPU1`, `output_name`添加`vnpu`后缀, 代表使用VNPU, 这时候模型速度会稍微慢些, 但是可以在设置中启动`AI-ISP`获取更好的摄像头画质
3. `npu_mode`也可以设置为`NPU2`, `output_name`添加`npu`后缀, 代表使用完整的NPU, 这时候模型速度最快, 但是必须在设置中关闭`AI-ISP`才能使用.

**④开始转换:**

在pulsar2容器内运行命令开始转换模型:
```bash
pulsar2 build --config config.json
```

⑤编写MUD文件:
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