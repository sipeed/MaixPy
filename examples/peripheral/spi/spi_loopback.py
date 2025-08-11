from maix import spi, pinmap, sys, err

# get pin and SPI number according to device id
device_id = sys.device_id()
if device_id == "maixcam2":
    pin_function = {
        "IO1_A21": "SPI2_CS1",
        "IO1_A19": "SPI2_MISO",
        "IO1_A18": "SPI2_MOSI",
        "IO1_A20": "SPI2_SCK"
    }
    spi_id = 2
else:
    pin_function = {
        "A24": "SPI4_CS",
        "A23": "SPI4_MISO",
        "A25": "SPI4_MOSI",
        "A22": "SPI4_SCK"
    }
    spi_id = 4

for pin, func in pin_function.items():
    err.check_raise(pinmap.set_pin_function(pin, func), f"Failed set pin{pin} function to {func}")


spidev = spi.SPI(spi_id, spi.Mode.MASTER, 1250000)

### Example of full parameter passing, fully documention see API documentation.
# spidev = spi.SPI(id=4,                  # SPI ID
#                  mode=spi.Mode.MASTER,  # SPI mode
#                  freq=1250000,          # SPI speed
#                  polarity=0,            # CPOL 0/1, default is 0
#                  phase=0,               # CPHA 0/1, default is 0
#                  bits=8,                # Bits of SPI, default is 8
#                  hw_cs=-1,              # use default hardware cs.
#                  soft_cs="",            # If you want use soft cs, set GPIO name,
#                                         # e.g.  GPIOA19(MaixCAM), GPIO0_A2(MaixCAM2)
#                                         # you should set pinmap first by yourself.
#                  cs_active_low=true     # cs pin active low voltage level

b = bytes(range(0, 8))

res = spidev.write_read(b, len(b))
if res == b:
    print("loopback test succeed")
else:
    print("loopback test failed")
    print(f"send:{b}\nread:{res}")