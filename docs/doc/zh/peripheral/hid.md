---
title: MaixCAM MaixPy 使用 USB HID（作为设备）
---

## 简介

HID（Human Interface Device）设备是一类计算机外围设备，用于向计算机传输输入数据，或从计算机接收输出数据。HID 设备最常见的例子包括键盘、鼠标、游戏控制器、触摸屏、和手写板等。HID 协议是一种用于人机交互设备的通信协议，它允许这些设备通过 USB、蓝牙或其他连接方式与主机进行数据交换。
MaixPy目前支持作为 USB HID 设备，比如作为键盘、鼠标和触摸屏给电脑使用，下面将会介入如何使用 MaixPy 通过 HID 来控制你的个人电脑～

> 如果你想将 USB 作为 host 模式以连接 HID 设备到 MaixCAM, 则在 `设置` 应用中将 USB 模式设置为 `host`模式即可。

## 一定要操作的前期准备

> MaixPy 固件版本应该 >= 4.5.1

在操作HID前一定要先使能HID设备，有两种方法：
1. 打开MaixCAM自带的`Settings`应用，依次点击`USB Settings`->勾选需要的HID设备，如`Keyboard`、`Mouse`、`Touchscreen`，然后点击`Confirm`后重启MaixCAM
2. 通过MaixVision中的`Examples/tools/maixcam_switch_usb_mode.py`示例，修改代码`device_list`中需要开启的HID设备，运行后重启MaixCAM
注意：由于最多只支持4个USB设备，因此在`ncm`，`rndis`，`keyboard`，`mouse`，`touchpad`之中只能同时启动4个设备，根据实际需求选择，其中`ncm`和`rndis`是USB网络协议设备，如果不需要可以关掉，默认是打开的。

## 用MaixPy编写一个键盘

需要使能了`HID Keyboard`后才能运行。

下面示例中，向PC发送按键事件

```python
from maix import hid, time

keyboard = hid.Hid(hid.DeviceType.DEVICE_KEYBOARD)

def press(keyboard, key):
    keyboard.write([0, 0, key, 0, 0, 0, 0, 0])
    time.sleep_ms(50)
    keyboard.write([0, 0, 0, 0, 0, 0, 0, 0])        #  key=0, means release

def press2(keyboard, key0 = 0, key1 = 0, key2 = 0, key3 = 0, key4 = 0, key5 = 0):
    keyboard.write([0, 0, key0, key1, key2, key3, key4, key5])
    time.sleep_ms(50)
    keyboard.write([0, 0, 0, 0, 0, 0, 0, 0])        #  key=0, means release

# key0: 0x1:left-ctrl 0x2:left-shift 0x4:left-alt 0x8:left-windows
#       0x10:right-ctrl 0x20:right-shift 0x40:right-alt 0x80:right-windows
def press3(keyboard, key0, key1):
    keyboard.write([key0, 0, key1, 0, 0, 0, 0, 0])
    time.sleep_ms(50)
    keyboard.write([0, 0, 0, 0, 0, 0, 0, 0])        #  key=0, means release

# 按键编号参考[USB HID文档](https://www.usb.org))的"Universal Serial Bus HID Usage Tables"部分
press(keyboard, 21)                 # press 'r'
press2(keyboard, 23, 24)            # press 'tu'
press3(keyboard, 0x2, 25)           # press 'left-shift + v'
```

创建`hid`对象后，通过`write`方法来发送按键事件，按键事件由一个8字节的数组表示，其中：

- 第1字节：指示 `ctrl`、`shift`、`alt` 等修饰键状态，字节每一位代表一个修饰键：`bit0： 左ctrl`，`bit1：左shift`， `bit2：左alt`，`bit3：左GUI（例如windows键）`，`bit4：右ctrl`，`bit5：右shift`，`bit6：右alt`，`bit7：右GUI`
- 第2字节：保留字节
- 第3字节：主按键值，0代表松开按键。按键编号参考[USB HID文档](https://www.usb.org))的"Universal Serial Bus HID Usage Tables"部分
- 第4～8字节：其他按键，可以用来实现一次按下多个按键，0代表松开按键

具体使用方法可以参考上面示例的代码

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
