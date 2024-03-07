from maix import camera, display, image

cam = camera.Camera()
cam.open(width = 640, height = 480)

screen = display.Display(device = None, width = 640, height = 480)
screen.open()

roi = [160, 120, 320, 240]
while 1:
    img = cam.read()

    qrcodes = img.find_qrcodes(roi)
    for a in qrcodes:
        # corners
        corners = a.corners()
        for i in range(4):
            img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_RED)

        # rect
        rect = a.rect()
        img.draw_rect(rect[0], rect[1], rect[2], rect[3], image.COLOR_BLUE)
        img.draw_text(rect[0] + 5, rect[1] + 5, "rect", image.COLOR_BLUE)

        # payload
        img.draw_text(a.x() + a.w() + 5, rect[1] + 20, "payload: " + a.payload(), image.COLOR_BLUE)

        # version
        img.draw_text(a.x() + a.w() + 5, rect[1] + 35, "version: " + str(a.version()), image.COLOR_BLUE)
        img.draw_text(a.x() + a.w() + 5, rect[1] + 50, "ecc_level: " + str(a.ecc_level()), image.COLOR_BLUE)
        img.draw_text(a.x() + a.w() + 5, rect[1] + 65, "mask: " + str(a.mask()), image.COLOR_BLUE)
        img.draw_text(a.x() + a.w() + 5, rect[1] + 80, "data_type: " + str(a.data_type()), image.COLOR_BLUE)
        img.draw_text(a.x() + a.w() + 5, rect[1] + 95, "eci: " + str(a.eci()), image.COLOR_BLUE)
        if a.is_numeric():
            img.draw_text(a.x() + a.w() + 5, rect[1] + 110, "is numeric", image.COLOR_BLUE)
        elif a.is_alphanumeric():
            img.draw_text(a.x() + a.w() + 5, rect[1] + 110, "is alphanumeric", image.COLOR_BLUE)
        elif a.is_binary():
            img.draw_text(a.x() + a.w() + 5, rect[1] + 110, "is binary", image.COLOR_BLUE)
        elif a.is_kanji():
            img.draw_text(a.x() + a.w() + 5, rect[1] + 110, "is kanji", image.COLOR_BLUE)
        else:
            img.draw_text(a.x() + a.w() + 5, rect[1] + 110, "is unknown", image.COLOR_BLUE)

    img.draw_rect(roi[0], roi[1], roi[2], roi[3], image.COLOR_GREEN)
    img.draw_text(roi[0] + 5, roi[1] + 5, "ROI", image.COLOR_GREEN)
    screen.show(img)
