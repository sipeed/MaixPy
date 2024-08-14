#!/usr/bin/env python

from maix.v1 import lcd, image
from maix import time

lcd.init()

# b_and
img = image.Image("/maixapp/share/icon/maixvision.png")
img2 = image.Image("/maixapp/share/icon/maixhub.png")
img.b_and(img2)
lcd.display(img)
time.sleep(1)

# b_nand
img = image.Image("/maixapp/share/icon/maixvision.png")
img2 = image.Image("/maixapp/share/icon/maixhub.png")
img.b_nand(img2)
lcd.display(img)
time.sleep(1)

# b_or
img = image.Image("/maixapp/share/icon/maixvision.png")
img2 = image.Image("/maixapp/share/icon/maixhub.png")
img.b_or(img2)
lcd.display(img)
time.sleep(1)

# b_nor
img = image.Image("/maixapp/share/icon/maixvision.png")
img2 = image.Image("/maixapp/share/icon/maixhub.png")
img.b_nor(img2)
lcd.display(img)
time.sleep(1)

# b_xor
img = image.Image("/maixapp/share/icon/maixvision.png")
img2 = image.Image("/maixapp/share/icon/maixhub.png")
img.b_xor(img2)
lcd.display(img)
time.sleep(1)

# b_xnor
img = image.Image("/maixapp/share/icon/maixvision.png")
img2 = image.Image("/maixapp/share/icon/maixhub.png")
img.b_xnor(img2)
lcd.display(img)
time.sleep(1)

while True:
    time.sleep(1)
