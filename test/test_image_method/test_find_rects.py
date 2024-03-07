from maix import camera, display, image

cam = camera.Camera()
cam.open(width = 640, height = 480)

screen = display.Display(device = None, width = 640, height = 480)
screen.open()

roi = [160, 120, 320, 240]
threshold = 2000
while 1:
    img = cam.read()

    rects = img.find_rects(roi, threshold)
    for a in rects:
        # corners
        corners = a.corners()
        for i in range(4):
            img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_RED)

        # rect
        rect = a.rect()
        img.draw_rect(rect[0], rect[1], rect[2], rect[3], image.COLOR_GREEN)
        img.draw_text(rect[0] + 5, rect[1] + 5, "rect", image.COLOR_GREEN)
        img.draw_text(rect[0] + 5, rect[1] + 20, "magnitude: " + str(a.magnitude()), image.COLOR_GREEN)

    img.draw_rect(roi[0], roi[1], roi[2], roi[3], image.COLOR_GREEN)
    img.draw_text(roi[0] + 5, roi[1] + 5, "ROI", image.COLOR_GREEN)
    screen.show(img)
