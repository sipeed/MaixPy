---
title: MaixCAM MaixPy 使用 HID 设备
---

## 简介

HID（Human Interface Device）设备是一类计算机外围设备，用于向计算机传输输入数据，或从计算机接收输出数据。HID 设备最常见的例子包括键盘、鼠标、游戏控制器、触摸屏、和手写板等。HID 协议是一种用于人机交互设备的通信协议，它允许这些设备通过 USB、蓝牙或其他连接方式与主机进行数据交换。MaixPy目前支持作为键盘、鼠标和触摸屏来使用，下面将会介入如何使用MaixPy通过HID来控制你的个人电脑～

## 一定要操作的前期准备

> MaixPy 固件版本应该 > 4.4.22(不包含)

在操作HID前一定要先使能HID设备，有两种方法：
1. 打开MaixCAM自带的`Settings`应用，依次点击`USB Settings`->勾选需要的HID设备，如`Keyboard`、`Mouse`、`Touchscreen`，然后点击`Confirm`后重启MaixCAM
2. 通过MaixVision中的`Examples/tools/maixcam_switch_usb_mode.py`示例，修改代码`device_list`中需要开启的HID设备，运行后重启MaixCAM
注意：由于最多只支持4个USB设备，因此在`ncm`，`rndis`，`keyboard`，`mouse`，`touchpad`之中只能同时启动4个设备，根据实际需求选择，其中`ncm`和`rndis`是USB网络协议设备，如果不需要可以关掉，默认是打开的。

## 用MaixPy编写一个键盘

需要使能了`HID Keyboard`后才能运行。

下面示例中，通过键盘发送`rstuv`四个字符，然后松开按键。

```python
from maix import hid, time

keyboard = hid.Hid(hid.DeviceType.DEVICE_KEYBOARD)

# 按键编号参考[USB HID文档](https://www.usb.org))的"Universal Serial Bus HID Usage Tables"部分
keys = [21, 22, 23, 24, 25, 0]    # 表示[r, s, t, u, v, 0], 0表示松开按键

for key in keys:
    keyboard.write([0, 0, key, 0, 0, 0, 0, 0])

```

## 用MaixPy编写一个鼠标

需要使能了`HID Mouse`后才能运行。

下面示例中，每隔100ms移动鼠标5个像素。

```python
from maix import hid, time

mouse = hid.Hid(hid.DeviceType.DEVICE_MOUSE)

button = 0      # 按键状态，0表示松开，1表示按下左键，2表示按下右键，4表示按下滚轮键
x_oft = 0       # 相对当前位置的偏移量，数值范围是-127~127
y_oft = 0       # 相对当前位置的偏移量，数值范围是-127~127
wheel_move = 0  # 滚轮移动距离，数值范围是-127~127

count = 0
while True:
    x_oft += 5
    y_oft += 5
    mouse.write([button, x_oft, y_oft, wheel_move])
    time.sleep_ms(100)
    count += 1
    if count > 50:
        break
```

## 用MaixPy编写一个触摸屏

需要使能了`HID Touchpad`后才能运行。

下面示例中，每隔100ms移动触摸屏150个单位，注意触摸屏的坐标系是绝对坐标，而不是相对坐标，另外需要将屏幕实际尺寸映射到[1, 0x7FFF]区间，坐标(1,1)表示左上角，坐标(0x7FFF,0x7FFF)表示右下角。

```python
from maix import hid, time

touchpad = hid.Hid(hid.DeviceType.DEVICE_TOUCHPAD)

def touchpad_set(button, x_oft, y_oft, wheel_move):
    touchpad.write([button,                             # 按键状态，0表示松开，1表示按下左键，2表示按下右键，4表示按下滚轮键
                    x_oft & 0xff, (x_oft >> 8) & 0xff,  # 绝对位置，最左为1, 最右为0x7fff，0表示不操作，数值范围是0～0x7fff
                    y_oft & 0xff, (y_oft >> 8) & 0xff,  # 绝对位置，最上为1, 最下为0x7fff，0表示不操作，数值范围是0～0x7fff
                    wheel_move])                        # 滚轮移动距离，数值范围是-127~127
button = 0
x_oft = 0
y_oft = 0
wheel_move = 0
count = 0
while True:
    x_oft += 150
    y_oft += 150
    touchpad_set(button, x_oft, y_oft, wheel_move)
    time.sleep_ms(100)
    count += 1
    if count > 50:
        break
```
