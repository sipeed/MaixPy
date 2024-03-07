from maix import camera, display, image

cam = camera.Camera(640, 480)
print("-- camera init ok")

disp = display.Display(640, 480)
print("-- display init ok")

disp_size = disp.size()
print("-- actually disp size: %dx%d" % (disp_size[0], disp_size[1]))

while 1:
    img = cam.read()
    img.draw_rect(0, 0, 50, 80, image.Color.from_rgb(255, 0, 0))
    if not disp.is_opened():
        break
    disp.show(img, fit = image.Fit.FIT_CONTAIN)
