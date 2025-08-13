from maix import image, display, touchscreen

class BechmarkBase:
    name = ""

    def __init__(self, disp : display.Display, ts : touchscreen.TouchScreen):
        pass

    def run(self, disp):
        return True, image.Image(disp.width(), disp.height())
