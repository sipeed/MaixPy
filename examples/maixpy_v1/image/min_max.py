#!/usr/bin/env python

from maix.v1 import lcd, image
from maix import time

lcd.init()

# min
img = image.Image("/maixapp/share/icon/maixvision.png")
img2 = image.Image("/maixapp/share/icon/maixhub.png")
img.min(img2)
lcd.display(img)
time.sleep(1)

# max
img = image.Image("/maixapp/share/icon/maixvision.png")
img2 = image.Image("/maixapp/share/icon/maixhub.png")
img.max(img2)
lcd.display(img)
time.sleep(1)

while True:
    time.sleep(1)
