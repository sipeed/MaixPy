# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import sys
import numbers
import numpy as np

from maix import spi, gpio, pinmap, time, err

__version__ = '0.0.4'

BG_SPI_CS_BACK = 0
BG_SPI_CS_FRONT = 1

SPI_CLOCK_HZ = 16000000

ST7789_NOP = 0x00
ST7789_SWRESET = 0x01
ST7789_RDDID = 0x04
ST7789_RDDST = 0x09

ST7789_SLPIN = 0x10
ST7789_SLPOUT = 0x11
ST7789_PTLON = 0x12
ST7789_NORON = 0x13

ST7789_INVOFF = 0x20
ST7789_INVON = 0x21
ST7789_DISPOFF = 0x28
ST7789_DISPON = 0x29

ST7789_CASET = 0x2A
ST7789_RASET = 0x2B
ST7789_RAMWR = 0x2C
ST7789_RAMRD = 0x2E

ST7789_PTLAR = 0x30
ST7789_MADCTL = 0x36
ST7789_COLMOD = 0x3A

ST7789_FRMCTR1 = 0xB1
ST7789_FRMCTR2 = 0xB2
ST7789_FRMCTR3 = 0xB3
ST7789_INVCTR = 0xB4
ST7789_DISSET5 = 0xB6

ST7789_GCTRL = 0xB7
ST7789_GTADJ = 0xB8
ST7789_VCOMS = 0xBB

ST7789_LCMCTRL = 0xC0
ST7789_IDSET = 0xC1
ST7789_VDVVRHEN = 0xC2
ST7789_VRHS = 0xC3
ST7789_VDVS = 0xC4
ST7789_VMCTR1 = 0xC5
ST7789_FRCTRL2 = 0xC6
ST7789_CABCCTRL = 0xC7

ST7789_RDID1 = 0xDA
ST7789_RDID2 = 0xDB
ST7789_RDID3 = 0xDC
ST7789_RDID4 = 0xDD

ST7789_GMCTRP1 = 0xE0
ST7789_GMCTRN1 = 0xE1

ST7789_PWCTR6 = 0xFC


class ST7789(object):
    """Representation of an ST7789 TFT LCD."""

    def __init__(self, port:int, dc:str, soft_cs:None|str=None, backlight:None|str=None, rst:None|str=None, width=240,
                 height=135, rotation=90, invert=True, spi_speed_hz=4000000,
                 offset_left=0,
                 offset_top=0):
        if rotation not in [0, 90, 180, 270]:
            raise ValueError("Invalid rotation {}".format(rotation))

        if width != height and rotation in [90, 270]:
            raise ValueError("Invalid rotation {} for {}x{} resolution".format(rotation, width, height))

        # print(f"use spi{port}")

        ### pinmap
        device_id = sys.device_id()
        if device_id == "maixcam2":
            if port == 1:
                spi_pin_function = {
                    "IO0_A2": "SPI1_CS0",
                    "IO0_A1": "SPI1_MISO",
                    "IO0_A0": "SPI1_MOSI",
                    "IO0_A4": "SPI1_SCK"
                }
            elif port == 2:
                spi_pin_function = {
                    "IO1_A21": "SPI2_CS1",
                    "IO1_A19": "SPI2_MISO",
                    "IO1_A18": "SPI2_MOSI",
                    "IO1_A20": "SPI2_SCK"
                }
            else:
                raise ValueError("Only support spi2 and spi4")
        else:
            if port == 4:
                spi_pin_function = {
                    "A24": "SPI4_CS",
                    "A23": "SPI4_MISO", # MISO
                    "A25": "SPI4_MOSI", # MOSI
                    "A22": "SPI4_SCK",  # SCK
                }
            elif port == 2:
                spi_pin_function = {
                    "P18": "SPI2_CS",
                    "P21": "SPI2_MISO", # MISO
                    "P22": "SPI2_MOSI", # MOSI
                    "P23": "SPI2_SCK",  # SCK
                }
            else:
                raise ValueError("Only support spi2 and spi4")
        for pin, func in spi_pin_function.items():
            err.check_raise(pinmap.set_pin_function(pin, func), f"Failed set pin{pin} function to {func}")

        ### soft cs
        if soft_cs != None:
            if 0 != pinmap.set_pin_function(soft_cs, f"GPIO{soft_cs}"):
                print(f"Failed: pin{pin}, func{func}")
                exit(-1)
            self._spi = spi.SPI(port, spi.Mode.MASTER, spi_speed_hz, 0, 0, 8, 0, True, soft_cs)
        else:
            self._spi = spi.SPI(port, spi.Mode.MASTER, spi_speed_hz)

        ### dc
        if 0 != pinmap.set_pin_function(dc, f"GPIO{dc}"):
            print(f"set DC failed: pin{dc}, funcGPIO{dc}")
        self._dc = gpio.GPIO(dc, gpio.Mode.OUT)
        self._dc.value(0)

        ### rst
        if rst is not None:
            pinmap.set_pin_function(rst, f"GPIO{rst}")
            self._rst = gpio.GPIO(rst, gpio.Mode.OUT)
            self.reset()

        ### backlight
        if backlight is not None:
            pinmap.set_pin_function(backlight, f"GPIO{backlight}")
            self._backlight = gpio.GPIO(backlight, gpio.Mode.OUT)
            self._backlight.value(0)
            time.sleep_ms(100)
            self._backlight.value(1)

        self._width = width
        self._height = height
        self._rotation = rotation
        self._invert = invert

        self._offset_left = offset_left
        self._offset_top = offset_top

        self._init()

    def send(self, data, is_data=True, chunk_size=4096):
        """Write a byte or array of bytes to the display. Is_data parameter
        controls if byte should be interpreted as display data (True) or command
        data (False).  Chunk_size is an optional size of bytes to write in a
        single SPI transaction, with a default of 4096.
        """
        # Set DC low for command, high for data.
        # self._dc.value(int(is_data))
        if is_data:
            self._dc.value(1)
        else:
            self._dc.value(0)
        # Convert scalar argument to list so either can be passed as parameter.
        if isinstance(data, numbers.Number):
            data = [data & 0xFF]
        # Write data a chunk at a time.
        for start in range(0, len(data), chunk_size):
            end = min(start + chunk_size, len(data))
            self._spi.write(bytes(data[start:end]))

    def set_backlight(self, value):
        """Set the backlight on/off."""
        if self._backlight is not None:
            self._backlight.value(value)

    @property
    def width(self):
        return self._width if self._rotation == 0 or self._rotation == 180 else self._height

    @property
    def height(self):
        return self._height if self._rotation == 0 or self._rotation == 180 else self._width

    def command(self, data):
        """Write a byte or array of bytes to the display as command data."""
        self.send(data, False)

    def data(self, data):
        """Write a byte or array of bytes to the display as display data."""
        self.send(data, True)

    def reset(self):
        """Reset the display, if reset pin is connected."""
        if self._rst is not None:
            self._rst.value(1)
            time.sleep_ms(500)
            self._rst.value(0)
            time.sleep_ms(500)
            self._rst.value(1)
            time.sleep_ms(500)

    def _init(self):
        # Initialize the display.

        self.command(ST7789_SWRESET)    # Software reset
        time.sleep_ms(150)               # delay 150 ms

        self.command(ST7789_MADCTL)
        self.data(0x70)

        self.command(ST7789_FRMCTR2)    # Frame rate ctrl - idle mode
        self.data(0x0C)
        self.data(0x0C)
        self.data(0x00)
        self.data(0x33)
        self.data(0x33)

        self.command(ST7789_COLMOD)
        self.data(0x05)

        self.command(ST7789_GCTRL)
        self.data(0x14)

        self.command(ST7789_VCOMS)
        self.data(0x37)

        self.command(ST7789_LCMCTRL)    # Power control
        self.data(0x2C)

        self.command(ST7789_VDVVRHEN)   # Power control
        self.data(0x01)

        self.command(ST7789_VRHS)       # Power control
        self.data(0x12)

        self.command(ST7789_VDVS)       # Power control
        self.data(0x20)

        self.command(0xD0)
        self.data(0xA4)
        self.data(0xA1)

        self.command(ST7789_FRCTRL2)
        self.data(0x0F)

        self.command(ST7789_GMCTRP1)    # Set Gamma
        self.data(0xD0)
        self.data(0x04)
        self.data(0x0D)
        self.data(0x11)
        self.data(0x13)
        self.data(0x2B)
        self.data(0x3F)
        self.data(0x54)
        self.data(0x4C)
        self.data(0x18)
        self.data(0x0D)
        self.data(0x0B)
        self.data(0x1F)
        self.data(0x23)

        self.command(ST7789_GMCTRN1)    # Set Gamma
        self.data(0xD0)
        self.data(0x04)
        self.data(0x0C)
        self.data(0x11)
        self.data(0x13)
        self.data(0x2C)
        self.data(0x3F)
        self.data(0x44)
        self.data(0x51)
        self.data(0x2F)
        self.data(0x1F)
        self.data(0x1F)
        self.data(0x20)
        self.data(0x23)

        if self._invert:
            self.command(ST7789_INVON)   # Invert display
        else:
            self.command(ST7789_INVOFF)  # Don't invert display

        self.command(ST7789_SLPOUT)

        self.command(ST7789_DISPON)     # Display on
        time.sleep_ms(100)               # 100 ms

    def begin(self):
        """Set up the display

        Deprecated. Included in __init__.

        """
        pass

    def set_window(self, x0=0, y0=0, x1=None, y1=None):
        """Set the pixel address window for proceeding drawing commands. x0 and
        x1 should define the minimum and maximum x pixel bounds.  y0 and y1
        should define the minimum and maximum y pixel bound.  If no parameters
        are specified the default will be to update the entire display from 0,0
        to width-1,height-1.
        """
        if x1 is None:
            x1 = self._width - 1

        if y1 is None:
            y1 = self._height - 1

        y0 += self._offset_top
        y1 += self._offset_top

        x0 += self._offset_left
        x1 += self._offset_left

        self.command(ST7789_CASET)       # Column addr set
        self.data(x0 >> 8)
        self.data(x0 & 0xFF)             # XSTART
        self.data(x1 >> 8)
        self.data(x1 & 0xFF)             # XEND
        self.command(ST7789_RASET)       # Row addr set
        self.data(y0 >> 8)
        self.data(y0 & 0xFF)             # YSTART
        self.data(y1 >> 8)
        self.data(y1 & 0xFF)             # YEND
        self.command(ST7789_RAMWR)       # write to RAM

    def display(self, image):
        """Write the provided image to the hardware.

        :param image: Should be RGB format and the same dimensions as the display hardware.

        """
        # Set address bounds to entire display.
        self.set_window()
        # Convert image to 16bit RGB565 format and
        # flatten into bytes.
        pixelbytes = self.image_to_data(image, self._rotation)
        # Write data to hardware.
        for i in range(0, len(pixelbytes), 4096):
            self.data(pixelbytes[i:i + 4096])

    def image_to_data(self, image, rotation=0):
        if not isinstance(image, np.ndarray):
            image = np.array(image.convert('RGB'))

        # Rotate the image
        pb = np.rot90(image, rotation // 90).astype('uint16')
        # Mask and shift the 888 RGB into 565 RGB
        red   = (pb[..., [0]] & 0xf8) << 8
        green = (pb[..., [1]] & 0xfc) << 3
        blue  = (pb[..., [2]] & 0xf8) >> 3

        # Stick 'em together
        result = red | green | blue

        # Output the raw bytes
        return result.byteswap().tobytes()


if __name__ == '__main__':
    """
    1.14” SPI screen with driver chip ST7789.
    You can buy this screen here.
    https://item.taobao.com/item.htm?id=610352268976

    |1|LEDA  |3V3    |
    |2|GND   |GND    |
    |3|RES   |3V3    |
    |4|RS(DC)|A14    |
    |5|SDA   |A25    |
    |6|SCL   |A22    |
    |7|VCC   |3V3    |
    |8|CS    |A24    |
    """

    import sys
    from PIL import Image
    from PIL import ImageDraw
    from maix import time

    ### Select a picture.
    image_file = "/maixapp/share/icon/detector.png"

    # get pin and spi number according to device id
    device_id = sys.device_id()
    if device_id == "maixcam2":
        spi_id = 2
    else:
        spi_id = 4

    disp = ST7789(
            height=135,
            rotation=0,
            port=spi_id,
            dc="A14",
            backlight=None,
            spi_speed_hz=1250000,
            offset_left=40,
            offset_top=53
        )


    WIDTH = disp.width
    HEIGHT = disp.height

    print(f"W{WIDTH}, H{HEIGHT}")

    # Initialize display.
    disp.begin()

    # Load an image.
    image = Image.open(image_file)

    # Resize the image
    image = image.resize((WIDTH, HEIGHT))

    disp.display(image)

    time.sleep(3)

    # Clear the display to a red background.
    # Can pass any tuple of red, green, blue values (from 0 to 255 each).
    # Get a PIL Draw object to start drawing on the display buffer.
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(255, 0, 0))

    draw = ImageDraw.Draw(img)

    # Draw a purple rectangle with yellow outline.
    draw.rectangle((10, 10, WIDTH - 10, HEIGHT - 10), outline=(255, 255, 0), fill=(255, 0, 255))

    # Draw some shapes.
    # Draw a blue ellipse with a green outline.
    draw.ellipse((10, 10, WIDTH - 10, HEIGHT - 10), outline=(0, 255, 0), fill=(0, 0, 255))

    # Draw a white X.
    draw.line((10, 10, WIDTH - 10, HEIGHT - 10), fill=(255, 255, 255))
    draw.line((10, HEIGHT - 10, WIDTH - 10, 10), fill=(255, 255, 255))

    # Draw a cyan triangle with a black outline.
    draw.polygon([(WIDTH / 2, 10), (WIDTH - 10, HEIGHT - 10), (10, HEIGHT - 10)], outline=(0, 0, 0), fill=(0, 255, 255))

    disp.display(img)