---
title: MaixCAM MaixPy 使用 I2C
---

> 注意需要 MaixPy 镜像和固件 >= 4.2.1

`MaixCAM` 的 `I2C` 及对应的 引脚 看图：

![](http://wiki.sipeed.com/hardware/zh/lichee/assets/RV_Nano/intro/RV_Nano_3.jpg)


对于 MaixCAM，由于引脚资源比较紧张，引出的 `I2C1` `I2C3` 引脚和 WiFi 模块（SDIO1）重合了，所以 WiFi 和硬件 I2C 只能二选一使用。
另外还有一个`I2C5`，是底层驱动软件模拟的，建议使用它，底层已经做好了驱动，使用时和使用硬件`I2C`一样。

默认`I2C5`的引脚是`GPIO`，所以使用`i2c`模块前先用`pinmap`设置以下引脚功能为`I2C5`：

```python
from maix import i2c, pinmap

pinmap.set_pin_function("A15", "I2C5_SCL")
pinmap.set_pin_function("A27", "I2C5_SDA")

bus1 = i2c.I2C(5, i2c.Mode.MASTER)
slaves = bus1.scan()
print("find slaves:", slaves)

```

更多 API 看 [i2c API 文档](https://wiki.sipeed.com/maixpy/api/maix/peripheral/i2c.html)



如上面所说， 对于 `MaixCAM` 硬件 `I2C` 和 `WiFi` 只能二选一，如果一定要用，需要禁用`WiFi`，使用`pinmap`模块设置引脚功能为 `I2C`，再使用`maix.i2c`模块操作。
> TODO: 提供禁用 WiFi 的方法（需要系统里面禁用掉 WiFi 驱动，比较复杂）

```python
from maix import i2c, pinmap

pinmap.set_pin_function("P18", "I2C1_SCL")
pinmap.set_pin_function("P21", "I2C1_SDA")

bus1 = i2c.I2C(1, i2c.Mode.MASTER)
slaves = bus1.scan()
print("find slaves:", slaves)

```



