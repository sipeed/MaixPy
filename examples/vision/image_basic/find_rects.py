from maix import camera, display, image, app

cam = camera.Camera(320, 240)
disp = display.Display()

while not app.need_exit():
    img = cam.read()

    rects = img.find_rects(threshold = 10000)
    for a in rects:
        # corners
        corners = a.corners()
        for i in range(4):
            img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_RED)
        # rect
        rect = a.rect()
        img.draw_rect(rect[0], rect[1], rect[2], rect[3], image.COLOR_RED)
        img.draw_string(rect[0] + 5, rect[1] + 5, "rect", image.COLOR_RED)
        img.draw_string(rect[0] + 5, rect[1] + 20, "magnitude: " + str(a.magnitude()), image.COLOR_RED)

    disp.show(img)
