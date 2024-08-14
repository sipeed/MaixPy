#!/usr/bin/env python

from maix.v1 import lcd, image
from maix import time

lcd.init()

# replace
img = image.Image("/maixapp/share/icon/maixvision.png")
img.replace(image = None, hmirror = False, vflip = True)
lcd.display(img)
time.sleep(1)

img = image.Image("/maixapp/share/icon/maixvision.png")
img.replace(image = None, hmirror = True, vflip = True)
lcd.display(img)
time.sleep(1)

img = image.Image("/maixapp/share/icon/maixvision.png")
img.replace(image = None, hmirror = True, vflip = False)
lcd.display(img)
time.sleep(1)

img = image.Image("/maixapp/share/icon/maixvision.png")
img.replace(image = None, hmirror = False, vflip = False)
lcd.display(img)
time.sleep(1)

while True:
    time.sleep(1)
