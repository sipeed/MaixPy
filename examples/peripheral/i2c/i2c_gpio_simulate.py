from maix import i2c, pinmap

# pinmap.set_pin_function("A15", "GPIOA23")
# pinmap.set_pin_function("A27", "GPIOA24")

bus1 = i2c.I2C(5, i2c.Mode.MASTER)
slaves = bus1.scan()
print("find slaves:", slaves)


# more API see https://wiki.sipeed.com/maixpy/api/maix/peripheral/i2c.html


