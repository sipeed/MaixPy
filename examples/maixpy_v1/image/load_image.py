#!/usr/bin/env python

from maix.v1 import lcd, image
from maix import time

lcd.init()

img = image.Image("/maixapp/share/icon/maixvision.png")
lcd.display(img)

while True:
    time.sleep(1)
