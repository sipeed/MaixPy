# Thermal160 历史记录

这是一个独立的 MaixCam2 应用包，用于长时间记录 Thermal160 运行温度。

## 功能

- 通过 MaixCam2 `/dev/ttyS2` 读取 Thermal160 UART 数据。
- 按 1 秒间隔采样温度历史，适合 24 小时运行观察。
- 持续保存 `output/history_*.csv`，避免长测中途断电丢失全部数据。
- 屏幕显示实时预览、当前温度和最近 30 分钟趋势。
- 点击右上角 `SAVE` 保存完整历史趋势图 PNG。
- 退出程序时，如果样本足够，会自动再保存一次 PNG。
- 启动 UART 前通过 MaixCAM2 `A9` / `GPIOA9` 给 Thermal160 发送一次软件复位脉冲。

## 软件复位

MaixCam2 电池供电时，Thermal160 可能不会自动上电/复位到可通信状态。程序启动时会执行：

1. `pinmap.set_pin_function("A9", "GPIOA9")`
2. `GPIOA9` 默认释放为高电平
3. 拉低约 `120ms`
4. 拉高释放并等待约 `400ms`

当前按“低有效复位”实现。如果硬件接法是高有效，需要在代码顶部对调：

```python
THERMAL_RESET_IDLE_LEVEL = 0
THERMAL_RESET_ACTIVE_LEVEL = 1
```

## 输出文件

- MaixCam2 安装运行时目录：`/maixapp/apps/thermal160_camera_history/output/`
- CSV：`/maixapp/apps/thermal160_camera_history/output/history_YYYYmmdd_HHMMSS.csv`
- PNG：`/maixapp/apps/thermal160_camera_history/output/trend_YYYYmmdd_HHMMSS.png`

## 协议

程序按当前 Thermal160 监控帧解析：

- 帧头：`0xFF`
- 像素：`160 * 120 = 19200` 字节
- telemetry：30 字节
- 总长度：`1 + 19200 + 30 = 19231` 字节

## 注意

- 这是历史记录应用，不替代实时热成像主应用。
- 需要在 MaixCam2 上实测 A9 复位、UART、触屏和 PNG 保存。
- 如果超过 3 秒仍没有合法帧，界面会显示 `thermal160 device not found`。
- A9 只能作为复位控制信号，不要用 MaixCAM2 GPIO 直接给 Thermal160 供电。
