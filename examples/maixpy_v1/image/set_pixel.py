#!/usr/bin/env python

from maix.v1 import image

img = image.Image("/maixapp/share/icon/maixvision.png")

# get old pixels
old_pixel = img.get_pixel(20, 50, True)
print('get old pixel, img({},{}) = {}'.format(20, 50, old_pixel))

# set new pixels
new_pixel = (10, 20, 30)
img.set_pixel(20, 50, new_pixel)
print('set new pixel, img({},{}) = {}'.format(20, 50, new_pixel))

# get curr pixels
curr_pixel = img.get_pixel(20, 50, True)
print('get curr pixel, img({},{}) = {}'.format(20, 50, curr_pixel))
