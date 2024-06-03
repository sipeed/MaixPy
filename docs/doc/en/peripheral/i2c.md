---
title: Using I2C with MaixPy
---

> Note: Requires MaixPy image and firmware >= 4.2.1

The `I2C` and corresponding pins of `MaixCAM` can be seen in the diagram:

![](http://wiki.sipeed.com/hardware/zh/lichee/assets/RV_Nano/intro/RV_Nano_3.jpg)

For MaixCAM, due to limited pin resources, the pins for `I2C1` and `I2C3` overlap with those of the WiFi module (SDIO1). Therefore, you can only use either WiFi or hardware I2C, but not both. Additionally, there is an `I2C5`, which is simulated by software at the lower driver level. It is recommended to use this one, as the drivers are already set up, and its use is the same as using hardware `I2C`.

By default, the pins for `I2C5` are configured as `GPIO`. Therefore, before using the `i2c` module, you should first use the `pinmap` module to set the pin functions to `I2C5` as follows:

```python
from maix import i2c, pinmap

pinmap.set_pin_function("A15", "I2C5_SCL")
pinmap.set_pin_function("A27", "I2C5_SDA")

bus1 = i2c.I2C(5, i2c.Mode.MASTER)
slaves = bus1.scan()
print("find slaves:", slaves)

```

For more APIs, see [i2c API documentation](https://wiki.sipeed.com/maixpy/api/maix/peripheral/i2c.html).

As mentioned above, for the `MaixCAM`, you must choose between using hardware `I2C` and `WiFi`. If you need to use `I2C`, you must disable `WiFi` and use the `pinmap` module to set the pin functions for `I2C`, then operate using the `maix.i2c` module.
> TODO: Provide a method to disable WiFi (requires disabling the WiFi driver in the system, which is more complex).

```python
from maix import i2c, pinmap

pinmap.set_pin_function("P18", "I2C1_SCL")
pinmap.set_pin_function("P21", "I2C1_SDA")

bus1 = i2c.I2C(1, i2c.Mode.MASTER)
slaves = bus1.scan()
print("find slaves:", slaves)

```