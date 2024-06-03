from maix import i2c, pinmap

pinmap.set_pin_function("A15", "I2C5_SCL")
pinmap.set_pin_function("A27", "I2C5_SDA")

bus = i2c.I2C(5, i2c.Mode.MASTER)
slaves = bus.scan()
print("find slaves:")
for s in slaves:
    print(f"{s}[0x{s:02x}]")


# more API see https://wiki.sipeed.com/maixpy/api/maix/peripheral/i2c.html


