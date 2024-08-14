#!/usr/bin/env python

from maix.v1 import lcd, image
from maix import time

lcd.init()

# linpolar
img = image.Image("/maixapp/share/icon/maixvision.png")
img.linpolar()
lcd.display(img)
time.sleep(1)

# logpolar
img = image.Image("/maixapp/share/icon/maixvision.png")
img.logpolar()
lcd.display(img)
time.sleep(1)

while True:
    time.sleep(1)
