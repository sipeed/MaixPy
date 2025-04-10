from maix import camera, display, app

cam = camera.Camera(160, 120)
disp = display.Display()

thresholds = [[0, 100, 20, 80, 10, 80]]

while not app.need_exit():
    img = cam.read()
    img.binary(thresholds)
    disp.show(img)