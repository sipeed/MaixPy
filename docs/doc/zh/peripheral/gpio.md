---
title: MaixPy 使用 GPIO
---

## 简介

使用 GPIO 可以控制引脚输入或者输出高低电平，用来读取信号或者输出控制信号，十分常用。

**注意** `MaixCAM` 的引脚是 `3.3V` 耐受，请勿输入 `5V` 电压。


## MaixPy 中使用 GPIO

> MaixPy 固件版本应该 > 4.1.2(不包含)

首先我们需要知道设备有哪些引脚和 GPIO，对于 MaixCAM 每个引脚都对应了一个 GPIO 控制器，如图：

![](http://wiki.sipeed.com/hardware/zh/lichee/assets/RV_Nano/intro/RV_Nano_3.jpg)

需要注意的是，引脚除了作为 GPIO 使用，还能用作其它功能比如 PWM 使用，使用前我们需要设置一下引脚的功能为 GPIO。

比如在 MaixCAM 上**有些引脚默认已经被其它功能占用，比如 UART0， WiFi(SDIO1 + A26), 不建议使用它们。**

其它的可以使用，另外 A14 引脚连接到了板载的 LED，默认是作为系统的负载提示灯，如果初始化它会自动取消系统提示灯功能作为普通 GPIO 被使用(注意`A14`只能作为输出)，这样你就能控制这颗 LED 的亮灭了。

```python
from maix import gpio, pinmap, time

pinmap.set_pin_function("A14", "GPIOA14")
led = gpio.GPIO("GPIOA14", gpio.Mode.OUT)
led.value(0)

while 1:
    led.toggle()
    time.sleep_ms(500)
```

这里先使用`pinmap`设置了`A14`引脚的功能为`GPIO`，当然，对于`A14`因为只有`GPIO`功能，可以不设置，为了程序通用起见，其它引脚可能需要设置，所以这里例程设置了。


更多 API 请看 [GPIO API 文档](https://wiki.sipeed.com/maixpy/api/maix/peripheral/gpio.html)


## GPIO 作为输入模式

```python
from maix import gpio, pinmap, time

pinmap.set_pin_function("A19", "GPIOA19")
led = gpio.GPIO("GPIOA19", gpio.Mode.IN)

while 1:
    print(led.value())
    time.sleep_ms(1) # sleep to make cpu free
```


