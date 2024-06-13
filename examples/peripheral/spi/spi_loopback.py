from maix import spi, pinmap

pin_function = {
    "A24": "SPI4_CS",
    "A23": "SPI4_MISO",
    "A25": "SPI4_MOSI",
    "A22": "SPI4_SCK"
}

for pin, func in pin_function.items():
    if 0 != pinmap.set_pin_function(pin, func):
        print(f"Failed: pin{pin}, func{func}")
        exit(-1)
        

spidev = spi.SPI(4, spi.Mode.MASTER, 1250000)

b = bytes(range(0, 8))

res = spidev.write_read(b, len(b))
if res == b:
    print("loopback test succeed")
else:
    print("loopback test failed")
    print(f"send:{b}\nread:{res}")