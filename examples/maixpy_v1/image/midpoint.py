#!/usr/bin/env python

from maix.v1 import lcd, image
from maix import time

lcd.init()

img = image.Image("/maixapp/share/icon/maixvision.png")
img.midpoint(2, bias = 0.5)
lcd.display(img)
time.sleep(1)

while True:
    time.sleep(1)
