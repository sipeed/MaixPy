from maix.peripheral import spi, pinmap

pinmap.set_pin_function("A24", "SPI1_CS")
pinmap.set_pin_function("A23", "SPI1_MISO")
pinmap.set_pin_function("A25", "SPI1_MOSI")
pinmap.set_pin_function("A22", "SPI1_SCK")

s = spi.SPI(1, spi.Mode.MASTER, 400000)

v = list(range(0, 32))

r = s.write_read(v, len(v))
if r != []:
    print(f"spi read {len(r)} bytes")
    print(f"read:{r}")
if r == v:
    print("The loopback test was successful.")
else:
    print("The loopback test failed")