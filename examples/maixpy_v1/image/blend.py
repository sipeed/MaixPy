#!/usr/bin/env python

from maix.v1 import lcd, image
from maix import time

lcd.init()

img = image.Image("/maixapp/share/icon/maixvision.png")
img2 = image.Image("/maixapp/share/icon/maixhub.png")
img.blend(img2, alpha=128)
lcd.display(img)
time.sleep(1)

while True:
    time.sleep(1)
