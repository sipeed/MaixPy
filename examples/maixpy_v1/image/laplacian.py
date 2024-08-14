#!/usr/bin/env python

from maix.v1 import lcd, image
from maix import time

size = 1
kernel = [-1, -2, -1, -2, 6, -2, -1, -2, -1]

lcd.init()
img = image.Image("/maixapp/share/icon/maixvision.png")
img.laplacian(2, mul = 1 / 8, add = 200)
lcd.display(img)

while True:
    time.sleep(1)
