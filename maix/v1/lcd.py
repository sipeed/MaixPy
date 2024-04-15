from maix import display as disp
from maix.v1 import image

__disp = None

def init(type=1, freq=15000000, color=0x000000, invert = 0, lcd_type = 0):
    global __disp
    __disp = disp.Display()
    pass

def deinit():
    pass

def width():
    return __disp.width()

def height():
    return __disp.height()

def type():
    raise ValueError('This operation is not supported')

def freq(freq):
    raise ValueError('This operation is not supported')

def set_backlight(value):
    __disp.set_backlight(value)

def get_backlight():
    raise ValueError('This operation is not supported')

def display(img, roi=None, oft=(0, 0)):
    __disp.show(img.get_priv_img())
    pass

def clear():
    img = image.Image(width=__disp.width(), height=__disp.height())
    img.clear()
    __disp.show(img.get_priv_img())
    pass

def rotation(dir):
    raise ValueError('This operation is not supported')

def direction(dir):
    rotation(dir)

def mirror(invert):
    __disp.set_hmirror(invert)

def flip(invert):
    __disp.set_vflip(invert)

def bgr_to_rgb(enable):
    raise ValueError('This operation is not supported')

def fill_rectangle(x, y, w, h, color):
    raise ValueError('This operation is not supported')

def set_jb_quality():
    raise ValueError('This operation is not supported\n')

