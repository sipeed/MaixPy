from maix import camera, display, image

cam = camera.Camera(480, 320)
disp = display.Display()

while 1:
    img = cam.read()

    barcodes = img.find_barcodes()
    for b in barcodes:
        rect = b.rect()
        img.draw_rect(rect[0], rect[1], rect[2], rect[3], image.COLOR_BLUE, 2)
        img.draw_string(0, 0, "payload: " + b.payload(), image.COLOR_GREEN)

    disp.show(img)