from maix import i2c, pinmap, sys


# get pin and i2c number according to device id
device_id = sys.device_id()
if device_id == "maixcam2":
    scl_pin_name = "IO0_A1"
    scl_i2c_id = "I2C6_SCL"
    sda_pin_name = "IO0_A0"
    sda_i2c_id = "I2C6_SDA"
    i2c_id = 6
else:
    scl_pin_name = "A15"
    scl_i2c_id = "I2C5_SCL"
    sda_pin_name = "A27"
    sda_i2c_id = "I2C5_SDA"
    i2c_id = 5

# set pinmap
pinmap.set_pin_function(scl_pin_name, scl_i2c_id)
pinmap.set_pin_function(sda_pin_name, sda_i2c_id)

bus = i2c.I2C(i2c_id, i2c.Mode.MASTER)
slaves = bus.scan()
print("find slaves:")
for s in slaves:
    print(f"{s}[0x{s:02x}]")


# more API see https://wiki.sipeed.com/maixpy/api/maix/peripheral/i2c.html


