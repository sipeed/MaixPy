from maix.v1 import image
from maix import camera

__camera = None

BAYER     = 0
RGB565    = 1
YUV422    = 2
GRAYSCALE = 3
JPEG      = 4
RGB888    = 5

# C/SIF Resolutions
QQCIF   = 1 # 88x72
QCIF    = 2 # 176x144
CIF     = 3 # 352x288
QQSIF   = 4 # 88x60
QSIF    = 5 # 176x120
SIF     = 6 # 352x240
# VGA Resolutions
QQQQVGA = 7 # 40x30
QQQVGA  = 8 # 80x60
QQVGA   = 9 # 160x120
QVGA    = 10 # 320x240
VGA     = 11 # 640x480
HQQQVGA = 12 # 60x40
HQQVGA  = 13 # 120x80
HQVGA   = 14 # 240x160
# Other
LCD     = 20 # 128x160
QQVGA2  = 21 # 128x160
WVGA    = 22 # 720x480
WVGA2   = 23 # 752x480
SVGA    = 24 # 800x600
SXGA    = 25 # 1280x1024
UXGA    = 26 # 1600x1200

def reset(freq=24000000, set_regs=True, dual_buff=True):
    global __camera
    __camera = camera.Camera()
    pass

def binocular_reset():
    raise ValueError('This operation is not supported')

def set_framesize(framesize, set_regs=True):
    w = 0
    h = 0
    if framesize == QQCIF:
        w = 88
        h = 72
    elif framesize == QCIF:
        w = 176
        h = 144
    elif framesize == CIF:
        w = 352
        h = 288
    elif framesize == QQSIF:
        w = 88
        h = 60
    elif framesize == QSIF:
        w = 176
        h = 120
    elif framesize == SIF:
        w = 352
        h = 240
    elif framesize == QQQQVGA:
        w = 40
        h = 30
    elif framesize == QQQVGA:
        w = 80
        h = 60
    elif framesize == QQVGA:
        w = 160
        h = 120
    elif framesize == QVGA:
        w = 320
        h = 240
    elif framesize == VGA:
        w = 640
        h = 480
    elif framesize == HQQQVGA:
        w = 60
        h = 40
    elif framesize == HQQVGA:
        w = 120
        h = 80
    elif framesize == HQVGA:
        w = 240
        h = 160
    elif framesize == LCD:
        w = 128
        h = 160
    elif framesize == QQVGA2:
        w = 128
        h = 160
    elif framesize == WVGA:
        w = 720
        h = 480
    elif framesize == WVGA2:
        w = 752
        h = 480
    elif framesize == SVGA:
        w = 800
        h = 600
    elif framesize == SXGA:
        w = 1280
        h = 1024
    elif framesize == UXGA:
        w = 1600
        h = 1200
    else:
        raise ValueError('This operation is not supported')
    return __camera.set_resolution(w, h)


def set_pixformat(format, set_regs=True):
    raise ValueError('This operation is not supported')

def run(enable=True):
    if enable:
        __camera.open()
    else:
        __camera.close()

def snapshot():
    img = __camera.read()
    v1_img = image.Image(do_nothing=True)
    v1_img.set_priv_img(img)
    return v1_img

def shutdown():
    raise ValueError('This operation is not supported')

def skip_frames(n):
    __camera.skip_frames(n)

def get_fb():
    raise ValueError('This operation is not supported')

def get_id():
    raise ValueError('This operation is not supported')

def set_hmirror(enable):
    __camera.hmirror(enable)

def set_vflip(enable):
    __camera.vflip(enable)

def set_brightness(brightness):
    brightness = brightness + 3
    val = brightness * 100 / 4
    __camera.luma(int(val))

def set_contrast(contrast):
    __camera.constrast(contrast)

def set_saturation(saturation):
    __camera.saturation(saturation)

def width():
    return __camera.width()

def height():
    return __camera.height()

def set_colorbar(enable):
    __camera.show_colorbar(enable)

def set_auto_gain(enable, gain_db=0):
    raise ValueError('This operation is not supported')

def get_gain_db():
    raise ValueError('This operation is not supported')

def __write_reg(addr, value):
    __camera.write_reg(addr, value)

def __read_reg(addr):
    return __camera.read_reg(addr)

def set_jb_quality():
    raise ValueError('This operation is not supported\n')




