# MaixCAM Thermal160 实时热成像监控

这是一个基于 MaixPy v4 的 MaixCAM2 Thermal160 实时热成像应用。程序通过 UART 接收 160x120 热成像帧，解析帧尾温度 telemetry，并实时渲染伪彩画面、中心点温度、最高/最低点和 NUC 状态。应用内置 24 小时历史记录模式，不再需要单独安装 history app。

## 硬件要求

* 设备：MaixCAM2。
* 传感器：Thermal160 / TN160 160x120 热成像模组。
* 连接方式：
  * UART：MaixCAM2 默认使用 `/dev/ttyS2`。
  * 波特率：初始 `2,000,000`，发送 `0x44` 握手后切到 `4,000,000`。
  * 复位：MaixCAM2 `A9` 配置为 `GPIOA9`，作为 Thermal160 软件复位脚。

## 启动行为

MaixCam2 电池供电时，Thermal160 可能不会自动上电/复位到可通信状态。应用启动 UART 前会自动执行一次 A9 软件复位：

1. `pinmap.set_pin_function("A9", "GPIOA9")`
2. `GPIOA9` 默认释放为高电平
3. 拉低约 `120ms`
4. 拉高释放并等待约 `400ms`

当前按“低有效复位”实现。如果硬件接法是高有效，需要在代码顶部对调：

```python
THERMAL_RESET_IDLE_LEVEL = 0
THERMAL_RESET_ACTIVE_LEVEL = 1
```

启动后前 3 秒显示 `Initializing thermal160` 和进度条；超过 3 秒仍没有合法帧，才显示 `thermal160 device not found`。

## 配置说明

在代码顶层可以根据需要调整以下常量：

* `SKIP_COUNT = 10`：启动后跳过的初始帧数。
* `STARTUP_GRACE_SEC = 3.0`：启动等待页到 `Device not found` 的延迟。
* `LONG_PRESS_SEC = 0.8`：长按右下角进入历史记录界面的触发时间。
* `SAMPLE_INTERVAL_SEC = 1.0`：历史记录采样间隔。
* `THERMAL_RESET_ASSERT_SEC = 0.12`：A9 复位保持时间。
* `THERMAL_RESET_RELEASE_DELAY_SEC = 0.40`：释放复位后的等待时间。

## 协议简介

程序期望的 UART 数据格式为：

* 帧头：`0xFF`
* 像素：`160 * 120 = 19200` 字节，8-bit 温度线性灰度
* telemetry：30 字节，包含 `VTEMP / t_lo / t_hi / anchor / smooth / mean_diff / NTC / NUC` 等运行状态
* 总长度：`1 + 19200 + 30 = 19231` 字节

注意：像素区允许出现合法的 `0xFF`。同步逻辑不能再用“payload 中出现 `0xFF` 就重同步”的旧方案，而是通过 telemetry 合理性和下一帧帧头位置校验。

## 历史记录模式

实时界面下：

* 短按右下角：切换伪彩色表。
* 长按右下角约 `0.8s`：进入历史记录界面。

历史记录界面下：

* 左上角 `BACK`：返回实时热成像界面。
* 右上角 `SAVE`：保存完整历史趋势图 PNG。

程序启动后会每秒后台记录一次温度到 CSV，进入 history 界面不会中断实时 UART 读取。

输出目录固定在当前 app 安装目录下：

* MaixCam2 安装运行时目录：`/maixapp/apps/thermal160_camera/output/`
* CSV：`/maixapp/apps/thermal160_camera/output/history_YYYYmmdd_HHMMSS.csv`
* PNG：`/maixapp/apps/thermal160_camera/output/trend_YYYYmmdd_HHMMSS.png`

## 注意事项

* A9 只能作为复位控制信号，不要用 MaixCAM2 GPIO 直接给 Thermal160 供电。
* 软件复位、电平有效性和等待时间需要结合实际硬件上板验证。
* 程序通过 `finally` 释放 UART 资源。
