#!/usr/bin/env python

from maix.v1 import lcd, image
from maix import time

size = 1
kernel = [-1, -2, -1, -2, 6, -2, -1, -2, -1]

lcd.init()
img = image.Image("/maixapp/share/icon/maixvision.png")
img.bilateral(2, color_sigma = 0.1, space_sigma = 1)
lcd.display(img)

while True:
    time.sleep(1)
