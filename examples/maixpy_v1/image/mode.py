#!/usr/bin/env python

from maix.v1 import lcd, image
from maix import time

lcd.init()

# difference
img = image.Image("/maixapp/share/icon/maixvision.png")
img.mode(2)
lcd.display(img)
time.sleep(1)

while True:
    time.sleep(1)
