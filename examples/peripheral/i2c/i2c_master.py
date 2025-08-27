from maix import i2c, pinmap, sys, err


# get pin and i2c number according to device id
device_id = sys.device_id()
if device_id == "maixcam2":
    scl_pin_name = "A1"
    scl_i2c_name = "I2C6_SCL"
    sda_pin_name = "A0"
    sda_i2c_name = "I2C6_SDA"
    i2c_id = 6
else:
    scl_pin_name = "A15"
    scl_i2c_name = "I2C5_SCL"
    sda_pin_name = "A27"
    sda_i2c_name = "I2C5_SDA"
    i2c_id = 5

# set pinmap
err.check_raise(pinmap.set_pin_function(scl_pin_name, scl_i2c_name), "set pin failed")
err.check_raise(pinmap.set_pin_function(sda_pin_name, sda_i2c_name), "set pin failed")

bus = i2c.I2C(i2c_id, i2c.Mode.MASTER)
slaves = bus.scan()
print("find slaves:")
for s in slaves:
    print(f"{s}[0x{s:02x}]")


# more API see https://wiki.sipeed.com/maixpy/api/maix/peripheral/i2c.html


