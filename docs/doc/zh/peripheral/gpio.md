---
title: MaixCAM MaixPy 使用 GPIO
---

## 简介

使用 GPIO 可以控制引脚输入或者输出高低电平，用来读取信号或者输出控制信号，十分常用。

**注意** `MaixCAM` 的引脚是 `3.3V` 耐受，**请勿**输入 `5V` 电压。


## 前置知识

请先学会使用[pinmap](./pinmap.md) 模块设置引脚功能。

要让一个引脚能使用 `GPIO` 功能，先用`pinmap`设置对应引脚功能为`GPIO`。

## 选择合适的 GPIO 使用

首先我们需要知道设备有哪些引脚和 GPIO，如图：

| 设备型号 | 引脚简图 | 引脚复用说明 |
| ------- | ------- | --- |
| MaixCAM | ![](https://wiki.sipeed.com/hardware/zh/lichee/assets/RV_Nano/intro/RV_Nano_3.jpg) | 板子丝印比如`A19`是引脚名，`GPIOA19/PWM7`是功能名 |
| MaixCAM-Pro | ![maixcam_pro_io](/static/image/maixcam_pro_io.png) | 第一个名如`A19`是引脚名，对应`GPIOA19/PWM7`是功能名 |
| MaixCAM2 | ![maixcam2_io](/static/image/maixcam2_io.png) | 第一个名如`A2`是引脚名，对应`GPIOA2/SPI1_CS0`是功能名，即使用`GPIO`功能只需要在`IO`名前面加一个`GPIO`即可。  |

需要注意的是，引脚默认可能用做其它用途，最好避开这些引脚，请看[pinmap](./pinmap.md) 文档中的说明。


## 电路注意点

注意引脚的电压耐受能力和负载能力有限，设计电路时需要注意，避免比如经常有新手问`为什么引脚不能直接让电机转动`等基础问题。

* **引脚电压耐压**：除非有特殊说明，引脚都是`3.3v`电平，请勿外接`5v`电压。
* **引脚输入输出电流**：芯片引脚的输入输出电流有限，一般只拿来作为控制信号，对于大电流需求的器件请使用转换电路。

**举例**：控制 LED 灯，简单的电路如下：
![](../../assets/gpio_led.png)
`LED` 直接由引脚输出高电平供电，这是最直观的使用方式，但是要十分小心，芯片引脚的输出和输入电流有上限，也就是驱动能力（一般在芯片手册中会描述），
这里电流为`3.3v/(LED+电阻 阻值)` < `0.64mA`， 所以能直接这样驱动，如果你的电路电流太大，就会驱动失败甚至导致芯片无法正常工作。

**正确的做法**是外接一个转换电路，让引脚只作为控制开关的信号，比如利用三极管/光耦/继电器转换等，这里不详细阐述，请自行扩展学习。


## GPIO 输出模式


LED 的电路图如图所示，所以我们只需要给 `A14`(`MaixCAM2` 是 ` A6`) 引脚一个高电平 LED 就会导通并亮起来：
![](../../assets/gpio_led.png)


```python
from maix import gpio, pinmap, time, sys, err

pin_name = "A6" if sys.device_id() == "maixcam2" else "A14"
gpio_name = "GPIOA6" if sys.device_id() == "maixcam2" else "GPIOA14"

err.check_raise(pinmap.set_pin_function(pin_name, gpio_name), "set pin failed")
led = gpio.GPIO(gpio_name, gpio.Mode.OUT)
led.value(0)

while 1:
    led.toggle()
    time.sleep_ms(500)
```

* 首先根据板子型号获得引脚和功能名。
* 使用`pinmap`设置了引脚的功能为`GPIO`。
* `err.check_raise` 用来检测`set_pin_function`的返回值，如果出错直接报错，防止我们手误写错了值。
* 初始化 `GPIO` 对象，设置为输出模式。
* 每隔`0.5s`翻转一次输出值，效果就是`LED`会交替闪烁。


更多 API 请看 [GPIO API 文档](https://wiki.sipeed.com/maixpy/api/maix/peripheral/gpio.html)


## GPIO 作为输入模式

```python
from maix import gpio, pinmap, time, err

err.check_raise(pinmap.set_pin_function("A19", "GPIOA19"), "set pin failed")
led = gpio.GPIO("GPIOA19", gpio.Mode.IN)

while 1:
    print(led.value())
    time.sleep_ms(1) # sleep to make cpu free
```

## MaixCAM-Pro 使用照明 LED

`MaixCAM / MaixCAM-Pro` 和 `MaixCAM2` 都有一个 LED 小灯，即接到了引脚 `A14` 和 `A6`，
另外 `MaixCAM-Pro` 和 `MaixCAM2` 还板载了一个`照明 LED`，分别连接到了 `B3` 和 `B25` 引脚，也是高电平开启低电平关闭：

```python
from maix import gpio, pinmap, time, sys, err

pin_name = "B25" if sys.device_id() == "maixcam2" else "B3"
gpio_name = "GPIOB25" if sys.device_id() == "maixcam2" else "GPIOB3"

err.check_raise(pinmap.set_pin_function(pin_name, gpio_name), "set pin failed")
led = gpio.GPIO(gpio_name, gpio.Mode.OUT)
led.value(0)

while 1:
    led.toggle()
    time.sleep_ms(500)

```

## 更多例程

看[MaixPy examples](https://github.com/sipeed/MaixPy/tree/main/examples/peripheral/gpio)。

## API 文档

更多 API 看 [GPIO API 文档](https://wiki.sipeed.com/maixpy/api/maix/peripheral/gpio.html)


