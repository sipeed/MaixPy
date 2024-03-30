from maix import camera, display, image

cam = camera.Camera()
cam.open(width = 640, height = 480)

screen = display.Display(device = None, width = 640, height = 480)
screen.open()

roi = [160, 120, 320, 240]
effort = 200
while 1:
    img = cam.read()

    datamatrices = img.find_datamatrices(roi, effort)
    for a in datamatrices:
        # corners
        corners = a.corners()
        for i in range(4):
            img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_RED, 2)

        # rect
        rect = a.rect()
        img.draw_rect(rect[0], rect[1], rect[2], rect[3], image.COLOR_BLUE, 2)
        img.draw_string(rect[0] + 5, rect[1] + 5, "rect", image.COLOR_BLUE)

        # payload
        img.draw_string(a.x() + a.w() + 5, rect[1] + 20, "payload: " + a.payload(), image.COLOR_RED)

        # rotation
        img.draw_string(a.x(), a.y() + 15, "rot: " + str(a.rotation()), image.COLOR_RED)

        # rows and columns
        img.draw_string(a.x(), a.y() + 30, "rows: " + str(a.rows()) + ", columns: " + str(a.columns()), image.COLOR_RED)

        # capacity
        img.draw_string(a.x(), a.y() + 45, "capacity: " + str(a.capacity()), image.COLOR_RED)

        # padding
        img.draw_string(a.x(), a.y() + 60, "padding: " + str(a.padding()), image.COLOR_RED)

    img.draw_rect(roi[0], roi[1], roi[2], roi[3], image.COLOR_GREEN)
    img.draw_string(roi[0] + 5, roi[1] + 5, "ROI", image.COLOR_GREEN)
    screen.show(img)
