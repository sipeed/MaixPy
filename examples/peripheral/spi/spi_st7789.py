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
|8|CS    |A27    |
"""

import sys
from PIL import Image
from PIL import ImageDraw
import st7789
from maix import time

image_file = "maixcam-logo.jpg"

disp = st7789.ST7789(
        height=135,
        rotation=0,
        port=4,
        dc="A14",
        soft_cs="A27",
        backlight=None,             
        spi_speed_hz=80000000,
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