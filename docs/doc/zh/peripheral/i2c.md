---
title: MaixPy 使用 I2C
---

对于 MaixCAM，由于引脚资源比较紧张，引出的 I2C 引脚和 WiFi 模块（SDIO1）重合了，所以 WiFi 和硬件 I2C 只能二选一使用。

所以推荐使用 IO 模拟 I2C。

> 注意需要 MaixPy 镜像和固件 > 4.1.2(不包含)

## IO 模拟 I2C

模拟 `I2C` 只需要引脚使用 `GPIO` 功能即可，在 `MaixCAM` 上，模拟 `I2C` 被固定在引脚`A15`(`SCL`)，`A27`(`SDA`)，并且`i2c`编号为`5`， 要使用，只需要:

```python
from maix import i2c, pinmap

# pinmap.set_pin_function("A15", "GPIOA23")
# pinmap.set_pin_function("A27", "GPIOA24")

bus1 = i2c.I2C(5, i2c.Mode.MASTER)
slaves = bus1.scan()
print("find slaves:", slaves)

```

更多 API 看 [i2c API 文档](https://wiki.sipeed.com/maixpy/api/maix/peripheral/i2c.html)


## 硬件 I2C

如上面所说， 对于 `MaixCAM` 硬件 `I2C` 和 `WiFi` 只能二选一，如果一定要用，需要禁用`WiFi`，使用`pinmap`模块设置引脚功能为 `I2C`，在使用`maix.i2c`模块操作。
> TODO: 提供禁用 WiFi 的方法（需要系统里面禁用掉 WiFi 驱动，比较复杂）

硬件`I2C`及对应的引脚看图：

![](http://wiki.sipeed.com/hardware/zh/lichee/assets/RV_Nano/intro/RV_Nano_3.jpg)

```python
from maix import i2c, pinmap

pinmap.set_pin_function("P18", "I2C1_SCL")
pinmap.set_pin_function("P21", "I2C1_SDA")

bus1 = i2c.I2C(1, i2c.Mode.MASTER)
slaves = bus1.scan()
print("find slaves:", slaves)

```



