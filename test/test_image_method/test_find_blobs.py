from maix import camera, display, image

cam = camera.Camera()
cam.open(width = 640, height = 480)

screen = display.Display(device = None, width = 640, height = 480)
screen.open()

roi = [160, 120, 320, 240]
area_threshold = 1000
pixels_threshold = 1000
thresholds = [[0, 100, -120, -10, 0, 30]]
invert = False
x_stride = 2
y_stride = 1
merge = True
margin = 10
x_hist_bins_max = 0
y_hist_bins_max = 0
while 1:
    img = cam.read()

    blobs = img.find_blobs(thresholds, invert, roi, x_stride, y_stride, area_threshold, pixels_threshold, merge, margin, x_hist_bins_max, y_hist_bins_max)
    for a in blobs:
        # draw corners
        corners = a.mini_corners()
        for i in range(4):
            img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_RED)

        # draw rect
        rect = a.rect()
        img.draw_rect(rect[0], rect[1], rect[2], rect[3], image.COLOR_GREEN)

        # corners
        corners = a.corners()
        for i in range(4):
            img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_RED)
        img.draw_text(corners[0][0] + 5, corners[0][1] + 5, "corners area: " + str(a.area()), image.COLOR_RED)

        # mini_corners
        mini_corners = a.mini_corners()
        for i in range(4):
            img.draw_line(mini_corners[i][0], mini_corners[i][1], mini_corners[(i + 1) % 4][0], mini_corners[(i + 1) % 4][1], image.COLOR_GREEN)
        img.draw_text(mini_corners[0][0] + 5, mini_corners[0][1] + 5, "mini_corners", image.COLOR_GREEN)

        # rect
        rect = a.rect()
        img.draw_rect(rect[0], rect[1], rect[2], rect[3], image.COLOR_BLUE)
        img.draw_text(rect[0] + 5, rect[1] + 5, "rect", image.COLOR_BLUE)

        # ...
        img.draw_text(a.x() + a.w() + 5, a.y(), "(" + str(a.x()) + "," + str(a.y()) + ")", image.COLOR_GREEN)
        img.draw_text(a.cx(), a.cy(), "(" + str(a.cx()) + "," + str(a.cy()) + ")", image.COLOR_GREEN)
        img.draw_text(a.x() + a.w() // 2, a.y(), str(a.w()), image.COLOR_GREEN)
        img.draw_text(a.x(), a.y() + a.h() // 2, str(a.h()), image.COLOR_GREEN)
        img.draw_text(a.x() + a.w() + 5, a.y() + 15, str(a.rotation_deg()), image.COLOR_GREEN)
        img.draw_text(a.x() + a.w() + 5, a.y() + 30, "code:" + str(a.code()) + ", count:" + str(a.count()), image.COLOR_GREEN)
        img.draw_text(a.x() + a.w() + 5, a.y() + 45, "perimeter:" + str(a.perimeter()), image.COLOR_GREEN)
        img.draw_text(a.x() + a.w() + 5, a.y() + 60, "roundness:" + str(a.roundness()), image.COLOR_GREEN)
        img.draw_text(a.x() + a.w() + 5, a.y() + 75, "elongation:" + str(a.elongation()), image.COLOR_GREEN)
        img.draw_text(a.x() + a.w() + 5, a.y() + 90, "area:" + str(a.area()), image.COLOR_GREEN)
        img.draw_text(a.x() + a.w() + 5, a.y() + 105, "density:" + str(round(a.density(), 2)), image.COLOR_GREEN)
        img.draw_text(a.x() + a.w() + 5, a.y() + 120, "extent:" + str(round(a.extent(), 2)), image.COLOR_GREEN)
        img.draw_text(a.x() + a.w() + 5, a.y() + 135, "compactness:" + str(round(a.compactness(), 2)), image.COLOR_GREEN)
        img.draw_text(a.x() + a.w() + 5, a.y() + 150, "solidity:" + str(a.solidity()), image.COLOR_GREEN)
        img.draw_text(a.x() + a.w() + 5, a.y() + 165, "convexity:" + str(a.convexity()), image.COLOR_GREEN)

        # major axis line
        major_axis_line = a.major_axis_line()
        img.draw_line(major_axis_line[0], major_axis_line[1], major_axis_line[2], major_axis_line[3], image.COLOR_RED)

        # minor axis line
        minor_axis_line = a.minor_axis_line()
        img.draw_line(minor_axis_line[0], minor_axis_line[1], minor_axis_line[2], minor_axis_line[3], image.COLOR_BLUE)

        # enclosing circle
        enclosing_circle = a.enclosing_circle()
        img.draw_circle(enclosing_circle[0], enclosing_circle[1], enclosing_circle[2], image.COLOR_RED)

        # enclosing ellipse
        enclosed_ellipse = a.enclosed_ellipse()
        img.draw_ellipse(enclosed_ellipse[0], enclosed_ellipse[1], enclosed_ellipse[2], enclosed_ellipse[3], enclosed_ellipse[4], 0, 360, image.COLOR_BLUE)

        # hist(not use)
        x_hist_bins = a.x_hist_bins()
        y_hist_bins = a.y_hist_bins()

    img.draw_rect(roi[0], roi[1], roi[2], roi[3], image.COLOR_GREEN)
    img.draw_text(roi[0] + 5, roi[1] + 5, "ROI", image.COLOR_GREEN)
    screen.show(img)
