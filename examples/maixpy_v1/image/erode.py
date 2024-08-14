#!/usr/bin/env python

from maix.v1 import lcd, image
from maix import time

lcd.init()

# erode
img = image.Image("/maixapp/share/icon/maixvision.png")
img.erode(2, -1)
lcd.display(img)
time.sleep(1)

# dilate
img = image.Image("/maixapp/share/icon/maixvision.png")
img.dilate(2, 0)
lcd.display(img)
time.sleep(1)

# open
img = image.Image("/maixapp/share/icon/maixvision.png")
img.open(2, 0)
lcd.display(img)
time.sleep(1)

# close
img = image.Image("/maixapp/share/icon/maixvision.png")
img.close(2, 0)
lcd.display(img)
time.sleep(1)

# top_hat
img = image.Image("/maixapp/share/icon/maixvision.png")
img.top_hat(2, 0)
lcd.display(img)
time.sleep(1)

# black_hat
img = image.Image("/maixapp/share/icon/maixvision.png")
img.black_hat(2, 0)
lcd.display(img)
time.sleep(1)

while True:
    time.sleep(1)
