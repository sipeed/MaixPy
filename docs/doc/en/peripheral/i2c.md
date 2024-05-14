---
title: MaixPy Using I2C
---

For MaixCAM, due to the tight pin resource constraints, the I2C pins overlap with the WiFi module (SDIO1), so you can only use either WiFi or hardware I2C, but not both.

Therefore, it is recommended to use IO emulation for I2C.

> Note: Requires MaixPy image and firmware > 4.1.2 (not included)

## IO Emulation I2C

To emulate `I2C`, you only need to use the `GPIO` functionality for the pins. On `MaixCAM`, the emulated `I2C` is fixed to pins `A15` (`SCL`) and `A27` (`SDA`), with the `i2c` number being `5`. To use it, simply:

```python
from maix import i2c, pinmap

# pinmap.set_pin_function("A15", "GPIOA23")
# pinmap.set_pin_function("A27", "GPIOA24")

bus1 = i2c.I2C(5, i2c.Mode.MASTER)
slaves = bus1.scan()
print("find slaves:", slaves)
```

More API visit [i2c API doc](https://wiki.sipeed.com/maixpy/api/maix/peripheral/i2c.html)

## Hardware I2C

As mentioned above, for `MaixCAM`, hardware `I2C` and `WiFi` are mutually exclusive. If you must use hardware `I2C`, you need to disable `WiFi` and use the `pinmap` module to set the pin functions to `I2C`, then use the `maix.i2c` module to operate.
> TODO: Provide a method to disable WiFi (requires disabling the WiFi driver in the system, which is relatively complex)

Hardware `I2C` and its correspond pin see:

![](http://wiki.sipeed.com/hardware/zh/lichee/assets/RV_Nano/intro/RV_Nano_3.jpg)

```python
from maix import i2c, pinmap

pinmap.set_pin_function("P18", "I2C1_SCL")
pinmap.set_pin_function("P21", "I2C1_SDA")

bus1 = i2c.I2C(1, i2c.Mode.MASTER)
slaves = bus1.scan()
print("find slaves:", slaves)
```
