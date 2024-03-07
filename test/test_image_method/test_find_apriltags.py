from maix import camera, display, image

cam = camera.Camera()
cam.open(width = 640, height = 480)

screen = display.Display(device = None, width = 640, height = 480)
screen.open()

roi = [160, 120, 320, 240]
families = image.ApriltagFamilies.TAG36H11
fx = float(-1)
fy = float(-1)
cx = 320
cy = 240
while 1:
    img = cam.read()

    apriltags = img.find_apriltags(roi, families, fx, fy, cx, cy)
    for a in apriltags:
        # corners
        corners = a.corners()
        for i in range(4):
            img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_RED, 2)

        # rect
        rect = a.rect()
        img.draw_rect(rect[0], rect[1], rect[2], rect[3], image.COLOR_BLUE, 2)
        img.draw_text(rect[0] + 5, rect[1] + 5, "rect", image.COLOR_BLUE)

        # apriltag
        img.draw_text(a.x() + a.w() + 5, rect[1] + 20, "id: " + str(a.id()), image.COLOR_RED)

        # family
        img.draw_text(a.x() + a.w() + 5, rect[1] + 35, "family: " + str(a.family()), image.COLOR_RED)

        # center coordinate
        img.draw_text(a.cx(), a.cy(), "(" + str(a.cx()) + "," + str(a.cy()) + ")", image.COLOR_RED)

        # rotation
        img.draw_text(a.cx(), a.cy() + 15, "rot: " + str(a.rotation()), image.COLOR_RED)

        # hamming
        img.draw_text(a.cx(), a.cy() + 30, "hamming: " + str(a.hamming()), image.COLOR_RED)

        # goodness
        img.draw_text(a.cx(), a.cy() + 45, "goodness: " + str(a.goodness()), image.COLOR_RED)

        # translation
        img.draw_text(a.cx(), a.cy() + 60, "translation: (" + str(round(a.x_translation(), 2)) + "," + str(round(a.y_translation(), 2)) + "," + str(round(a.z_translation(), 2)) + ")", image.COLOR_RED)

        # rotation
        img.draw_text(a.cx(), a.cy() + 75, "rotation: (" + str(round(a.x_rotation(), 2)) + "," + str(round(a.y_rotation(), 2)) + "," + str(round(a.z_rotation(), 2)) + ")", image.COLOR_RED)

    img.draw_rect(roi[0], roi[1], roi[2], roi[3], image.COLOR_GREEN)
    img.draw_text(roi[0] + 5, roi[1] + 5, "ROI", image.COLOR_GREEN)
    screen.show(img)
