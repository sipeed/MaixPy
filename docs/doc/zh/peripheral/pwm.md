---
title: MaixCAM MaixPy 使用 PWM
update:
  - date: 2025-08-08
    author: Neucrack
    version: 1.1.0
    content: 重构文档，更以于初学者理解
---

## 前置知识

请先学会使用[pinmap](./pinmap.md) 模块设置引脚功能。

要让一个引脚能使用 `PWM` 功能，先用`pinmap`设置对应引脚功能为`PWM`。


## PWM 简介

使用 `PWM` 可以通过一个引脚输出一个方波，设置合适的周期和占空比（低电平占整个周期的比例）可以在不同场景中发挥作用，比如：
* 控制舵机转向。
* 控制无刷电机旋转速度。
* 控制灯光亮度（PWM 调光）。

关于更多 PWM 基础知识，网上有很多好教程，本文不展开讲解，请自行搜索学习。


## 选择合适的 PWM 使用

首先我们需要知道设备有哪些引脚和 PWM，如图：

| 设备型号 | 引脚简图 | 引脚复用说明 |
| ------- | ------- | --- |
| MaixCAM | ![](https://wiki.sipeed.com/hardware/zh/lichee/assets/RV_Nano/intro/RV_Nano_3.jpg) | 板子丝印比如`A19`是引脚名，`PWM7`是功能名 |
| MaixCAM-Pro | ![maixcam_pro_io](/static/image/maixcam_pro_io.png) | 第一个名如`A19`是引脚名，对应`PWM7`是功能名 |
| MaixCAM2 | ![maixcam2_io](/static/image/maixcam2_io.png) | 第一个名如`B25`是引脚名，对应`PWM6`是功能名  |

需要注意的是，引脚默认可能用做其它用途，最好避开这些引脚，请看[pinmap](./pinmap.md) 文档中的说明。

比如：
* `MaixCAM/MaixCAM-Pro`: 因为`WiFi` 使用了`SDIO1`的所有引脚，所以`PWM4~9`不建议使用。
* `MaixCAM2`: 默认有 4个 PWM 引脚可以直接使用，照明 LED 也可以用`PWM6` 控制，注意`PWM6` 只能在`A30`和照明 LED 二选一使用。


## MaixPy 使用 PWM 控制 LED 亮度

利用人眼的暂留效应，一直打开 LED 就是最亮，不停高速开关 LED 就能实现调亮度，关的时间占比越长就越暗。

```python
from maix import pwm, time, pinmap, sys, err


# get pin and pwm number according to device id
device_id = sys.device_id()
if device_id == "maixcam2":
    pin_name = "B25" # LED light
    pwm_id = 6
else:
    pin_name = "A18" # A18 pin
    pwm_id = 6

# set pinmap
err.check_raise(pinmap.set_pin_function(pin_name, f"PWM{pwm_id}"), "set pinmap failed")


SERVO_PERIOD = 100000     # 100kHz 0.01ms

out = pwm.PWM(pwm_id, freq=SERVO_PERIOD, duty=0, enable=True)

for i in range(100):
    print(i)
    out.duty(i)
    time.sleep_ms(100)

for i in range(100):
    print(100 - i)
    out.duty(100 - i)
    time.sleep_ms(100)
```


## MaixPy 使用 PWM 控制舵机

控制舵机角度就是控制占空比，不同占空比对应不同角度，可以看舵机的文档。

现在控制舵机从最小角度旋转到最大角度再旋转回最小角度：

```python
from maix import pwm, time, pinmap, err

SERVO_PERIOD = 50     # 50Hz 20ms
SERVO_MIN_DUTY = 2.5  # 2.5% -> 0.5ms
SERVO_MAX_DUTY = 12.5  # 12.5% -> 2.5ms


# get pin and pwm number according to device id
device_id = sys.device_id()
if device_id == "maixcam2":
    pin_name = "A31"
    pwm_id = 7
else:
    pin_name = "A19"
    pwm_id = 7

# set pinmap
err.check_raise(pinmap.set_pin_function(pin_name, f"PWM{pwm_id}"), "set pinmap failed")



def angle_to_duty(percent):
    return (SERVO_MAX_DUTY - SERVO_MIN_DUTY) * percent / 100.0 + SERVO_MIN_DUTY


out = pwm.PWM(pwm_id, freq=SERVO_PERIOD, duty=angle_to_duty(0), enable=True)

for i in range(100):
    out.duty(angle_to_duty(i))
    time.sleep_ms(100)

for i in range(100):
    out.duty(angle_to_duty(100 - i))
    time.sleep_ms(100)
```


## 更多例程

看[MaixPy examples](https://github.com/sipeed/MaixPy/tree/main/examples/peripheral/pwm)。


## API 文档

更多 API 看 [PWM API 文档](https://wiki.sipeed.com/maixpy/api/maix/peripheral/pwm.html)



