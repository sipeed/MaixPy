#!/usr/bin/env python

from maix.v1 import lcd, image
from maix import time

from maix import image as maix_img

lcd.init()
img = image.Image("test.jpg")

print('invert format to grayscale')
img.to_grayscale()
lcd.display(img)
time.sleep(1)

print('invert format to rgb888')
img.to_rgb888()
lcd.display(img)
time.sleep(1)

rgb=(100,200,30)
lab=image.rgb_to_lab(rgb)
print('rgb to lab, res:', lab)

rgb=image.lab_to_rgb(lab)
print('lab to rgb, res:', rgb)

rgb=(10,20,30)
gray=image.rgb_to_grayscale(rgb)
print('rgb to gray, res:', gray)

rgb=image.grayscale_to_rgb(gray)
print('gray to rgb, res:', rgb)

while True:
    time.sleep(1)
