---
title: MaixPy 使用 PWM
---


## 简介

在 MaixPy (v4) 中使用 `PWM`，先使用`pinmap`设置引脚的功能为 `PWM`，在使用。

以及每个 `PWM` 有对应的引脚，根据 MaixCAM 的引脚图可以看到:

![](http://wiki.sipeed.com/hardware/zh/lichee/assets/RV_Nano/intro/RV_Nano_3.jpg)

这里我们推荐使用`PWM6` 和 `PWM7`。

对于 `MaixCAM` 因为`WiFi` 使用了`SDIO1`的所有引脚，所以`PWM4~9`只能和`WiFi`二选一使用。
> TODO: 提供禁用 WiFi 的方法（需要系统里面禁用掉 WiFi 驱动，比较复杂）


## MaixPy 使用 PWM 控制舵机

这里我们以控制舵机为例， 使用`MaixCAM`的`PWM7`和`A19`引脚：

```python
from maix import pwm, time, pinmap

SERVO_PERIOD = 50     # 50Hz 20ms
SERVO_MIN_DUTY = 2.5  # 2.5% -> 0.5ms
SERVO_MAX_DUTY = 12.5  # 12.5% -> 2.5ms

# Use PWM7
pwm_id = 7
# !! set pinmap to use PWM7
pinmap.set_pin_function("A19", "PWM7")



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

这里的功能是控制舵机从最小角度旋转到最大角度再旋转回最小角度。



