---
title: Introduction to Using MaixCAM MaixPy USB HID (as device)
---


## 简介

MaixPy currently supports simulate as USB HID device like keyboards, mice, and touchscreens, and the following is a guide on how to use maixPy to control your PC via HID.

> If you want to use USB as host to connect HID devices into MaixCAM, set USB mode to HOST mode in `settings`.

## Preparation

> MaixPy firmware version should be >= 4.5.1.

You must enable the HID device before operating HID, there are two ways:
1. Open the `Settings` application that comes with MaixCAM, click `USB Settings` in turn -> tick the required HID devices, such as `Keyboard`, `Mouse`, `Touchscreen`, and then click `Confirm` , then restart MaixCAM.
2. Through the `Examples/tools/maixcam_switch_usb_mode.py` in MaixVision, modify the HID devices that need to be switched on in the `device_list`, run it and restart MaixCAM.
Note: Since only 4 USB devices are supported, only 4 devices can be started at the same time among `ncm`, `rndis`, `keyboard`, `mouse`, `touchpad`, choose according to the actual demand, among them, `ncm` and `rndis` are the USB network protocol devices, you can turn them off if you don't need them, by default, they are turned on.

## Write a keyboard in MaixPy.

You need to enable `HID Keyboard` to run it.

The following example sends keyboard event to pc.

```python
from maix import hid, time

keyboard = hid.Hid(hid.DeviceType.DEVICE_KEYBOARD)

# Refer to the `Universal Serial Bus HID Usage Tables` section of the [USB HID Documentation](https://www.usb.org) for key numbers.
keys = [21, 22, 23, 24, 25, 0]   # means [r, s, t, u, v, 0], 0 means release key.

for key in keys:
    keyboard.write([0, 0, key, 0, 0, 0, 0, 0])

```

After creating the `hid` object, key events can be sent using the `write` method. A key event is represented by an 8-byte array, where:
- **Byte 1**: Indicates the status of modifier keys like `ctrl`, `shift`, `alt`, etc. Each bit represents a specific modifier key:`bit0: left ctrl`,`bit1: left shift`,`bit2: left alt`,`bit3: left GUI (e.g., Windows key)`,`bit4: right ctrl`,`bit5: right shift`,`bit6: right alt`,`bit7: right GUI`
- **Byte 2**: Reserved byte.
- **Byte 3**: Primary key value. A value of 0 means the key is released. Key codes are referenced from the "Universal Serial Bus HID Usage Tables" section of the [USB HID documentation](https://www.usb.org).
- **Bytes 4~8**: Additional keys, used to press multiple keys at once. A value of 0 means the key is released.

For specific usage, refer to the example code above.

## Write a mouse in MaixPy.

You need to enable `HID Mouse` to run it.

The following example moves the mouse 5 pixels every 100ms.

```python
from maix import hid, time

mouse = hid.Hid(hid.DeviceType.DEVICE_MOUSE)

button = 0      # button state, 0 means release, 1 means left button pressed, 2 means right button pressed, 4 means wheel button pressed
x_oft = 0       # offset relative to current position, value range is -127~127
y_oft = 0       # offset relative to current position, value range is -127~127
wheel_move = 0  # The distance the wheel has moved, the range of values is -127~127

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

## Write a touchpad in MaixPy.

The `HID Touchpad` needs to be enabled to run.

In the following example, move the touchscreen 150 units every 100ms. Note that the coordinate system of the touchscreen is absolute, not relative, and that you need to map the actual size of the screen to the interval [1, 0x7FFF], the coordinates (1,1) means the upper left corner, the coordinates (0x7FFF,0x7FFF) means the lower right corner.

```python
from maix import hid, time

touchpad = hid.Hid(hid.DeviceType.DEVICE_TOUCHPAD)

def touchpad_set(button, x_oft, y_oft, wheel_move):
    touchpad.write([button,                             # button state, 0 means release, 1 means left button pressed, 2 means right button pressed, 4 means wheel button pressed
                    x_oft & 0xff, (x_oft >> 8) & 0xff,  # Absolute position, the leftmost is 1, the rightmost is 0x7fff, 0 means no operation, the value range is 0 to 0x7fff.
                    y_oft & 0xff, (y_oft >> 8) & 0xff,  # Absolute position, the topmost is 1, the bottom is 0x7fff, 0 means no operation, the value range is 0 to 0x7fff
                    wheel_move])                        # wheel move distance, value range is -127~127
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

