#!/usr/bin/env python

from maix.v1 import lcd, sensor
from maix import time
import math

lcd.init()
sensor.reset()
sensor.set_framesize(sensor.QVGA)
sensor.run(1)

thresholds = [[0, 80, 40, 80, 10, 80]]      # red

while True:
    img = sensor.snapshot()

    blobs = img.find_blobs(thresholds)
    for a in blobs:
        # draw rect
        rect = a.rect()
        img.draw_rectangle(rect[0], rect[1], rect[2], rect[3], (0,255,0))

        # corners
        corners = a.corners()
        for i in range(4):
            img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], (255,0,0))
        img.draw_string(corners[0][0] + 5, corners[0][1] + 5, "corners area: " + str(a.area()), (255,0,0))

        # mini_corners
        mini_corners = a.mini_corners()
        for i in range(4):
            img.draw_line(mini_corners[i][0], mini_corners[i][1], mini_corners[(i + 1) % 4][0], mini_corners[(i + 1) % 4][1], (0,255,0))
        img.draw_string(mini_corners[0][0] + 5, mini_corners[0][1] + 5, "mini_corners", (0,255,0))

        # rect
        rect = a.rect()
        img.draw_rectangle(rect[0], rect[1], rect[2], rect[3], (0,0,255))
        img.draw_string(rect[0] + 5, rect[1] + 5, "rect", (0,0,255))

        # ...
        img.draw_string(a.x() + a.w() + 5, a.y(), "(" + str(a.x()) + "," + str(a.y()) + ")", (0,255,0))
        img.draw_string(a.cx(), a.cy(), "(" + str(a.cx()) + "," + str(a.cy()) + ")", (0,255,0))
        img.draw_string(a.x() + a.w() // 2, a.y(), str(a.w()), (0,255,0))
        img.draw_string(a.x(), a.y() + a.h() // 2, str(a.h()), (0,255,0))
        img.draw_string(a.x() + a.w() + 5, a.y() + 15, str(a.rotation_deg()), (0,255,0))
        img.draw_string(a.x() + a.w() + 5, a.y() + 30, "code:" + str(a.code()) + ", count:" + str(a.count()), (0,255,0))
        img.draw_string(a.x() + a.w() + 5, a.y() + 45, "perimeter:" + str(a.perimeter()), (0,255,0))
        img.draw_string(a.x() + a.w() + 5, a.y() + 60, "roundness:" + str(a.roundness()), (0,255,0))
        img.draw_string(a.x() + a.w() + 5, a.y() + 75, "elongation:" + str(a.elongation()), (0,255,0))
        img.draw_string(a.x() + a.w() + 5, a.y() + 90, "area:" + str(a.area()), (0,255,0))
        img.draw_string(a.x() + a.w() + 5, a.y() + 105, "density:" + str(round(a.density(), 2)), (0,255,0))
        img.draw_string(a.x() + a.w() + 5, a.y() + 120, "extent:" + str(round(a.extent(), 2)), (0,255,0))
        img.draw_string(a.x() + a.w() + 5, a.y() + 135, "compactness:" + str(round(a.compactness(), 2)), (0,255,0))
        img.draw_string(a.x() + a.w() + 5, a.y() + 150, "solidity:" + str(a.solidity()), (0,255,0))
        img.draw_string(a.x() + a.w() + 5, a.y() + 165, "convexity:" + str(a.convexity()), (0,255,0))

        # major axis line
        major_axis_line = a.major_axis_line()
        img.draw_line(major_axis_line[0], major_axis_line[1], major_axis_line[2], major_axis_line[3], (255,0,0))

        # minor axis line
        minor_axis_line = a.minor_axis_line()
        img.draw_line(minor_axis_line[0], minor_axis_line[1], minor_axis_line[2], minor_axis_line[3], (0,0,255))

        # enclosing circle
        enclosing_circle = a.enclosing_circle()
        img.draw_circle(enclosing_circle[0], enclosing_circle[1], enclosing_circle[2], (255,0,0))

        # enclosing ellipse
        enclosed_ellipse = a.enclosed_ellipse()
        img.draw_ellipse(enclosed_ellipse[0], enclosed_ellipse[1], enclosed_ellipse[2], enclosed_ellipse[3], enclosed_ellipse[4], (0,0,255))

        # hist(not use)
        x_hist_bins = a.x_hist_bins()
        y_hist_bins = a.y_hist_bins()

    lcd.display(img)



# from maix import camera, display, image

# cam = camera.Camera()
# cam.open(width = 640, height = 480)

# screen = display.Display(device = None, width = 640, height = 480)
# screen.open()

# roi = [160, 120, 320, 240]
# area_threshold = 1000
# pixels_threshold = 1000
# thresholds = [[0, 100, -120, -10, 0, 30]]
# invert = False
# x_stride = 2
# y_stride = 1
# merge = True
# margin = 10
# x_hist_bins_max = 0
# y_hist_bins_max = 0
# while 1:
#     img = cam.read()

#     blobs = img.find_blobs(thresholds, invert, roi, x_stride, y_stride, area_threshold, pixels_threshold, merge, margin, x_hist_bins_max, y_hist_bins_max)
#     for a in blobs:
#         # draw rect
#         rect = a.rect()
#         img.draw_rectangle(rect[0], rect[1], rect[2], rect[3], (0,255,0))

#         # corners
#         corners = a.corners()
#         for i in range(4):
#             img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], (255,0,0))
#         img.draw_string(corners[0][0] + 5, corners[0][1] + 5, "corners area: " + str(a.area()), (255,0,0))

#         # mini_corners
#         mini_corners = a.mini_corners()
#         for i in range(4):
#             img.draw_line(mini_corners[i][0], mini_corners[i][1], mini_corners[(i + 1) % 4][0], mini_corners[(i + 1) % 4][1], (0,255,0))
#         img.draw_string(mini_corners[0][0] + 5, mini_corners[0][1] + 5, "mini_corners", (0,255,0))

#         # rect
#         rect = a.rect()
#         img.draw_rectangle(rect[0], rect[1], rect[2], rect[3], (0,0,255))
#         img.draw_string(rect[0] + 5, rect[1] + 5, "rect", (0,0,255))

#         # ...
#         img.draw_string(a.x() + a.w() + 5, a.y(), "(" + str(a.x()) + "," + str(a.y()) + ")", (0,255,0))
#         img.draw_string(a.cx(), a.cy(), "(" + str(a.cx()) + "," + str(a.cy()) + ")", (0,255,0))
#         img.draw_string(a.x() + a.w() // 2, a.y(), str(a.w()), (0,255,0))
#         img.draw_string(a.x(), a.y() + a.h() // 2, str(a.h()), (0,255,0))
#         img.draw_string(a.x() + a.w() + 5, a.y() + 15, str(a.rotation_deg()), (0,255,0))
#         img.draw_string(a.x() + a.w() + 5, a.y() + 30, "code:" + str(a.code()) + ", count:" + str(a.count()), (0,255,0))
#         img.draw_string(a.x() + a.w() + 5, a.y() + 45, "perimeter:" + str(a.perimeter()), (0,255,0))
#         img.draw_string(a.x() + a.w() + 5, a.y() + 60, "roundness:" + str(a.roundness()), (0,255,0))
#         img.draw_string(a.x() + a.w() + 5, a.y() + 75, "elongation:" + str(a.elongation()), (0,255,0))
#         img.draw_string(a.x() + a.w() + 5, a.y() + 90, "area:" + str(a.area()), (0,255,0))
#         img.draw_string(a.x() + a.w() + 5, a.y() + 105, "density:" + str(round(a.density(), 2)), (0,255,0))
#         img.draw_string(a.x() + a.w() + 5, a.y() + 120, "extent:" + str(round(a.extent(), 2)), (0,255,0))
#         img.draw_string(a.x() + a.w() + 5, a.y() + 135, "compactness:" + str(round(a.compactness(), 2)), (0,255,0))
#         img.draw_string(a.x() + a.w() + 5, a.y() + 150, "solidity:" + str(a.solidity()), (0,255,0))
#         img.draw_string(a.x() + a.w() + 5, a.y() + 165, "convexity:" + str(a.convexity()), (0,255,0))

#         # major axis line
#         major_axis_line = a.major_axis_line()
#         img.draw_line(major_axis_line[0], major_axis_line[1], major_axis_line[2], major_axis_line[3], (255,0,0))

#         # minor axis line
#         minor_axis_line = a.minor_axis_line()
#         img.draw_line(minor_axis_line[0], minor_axis_line[1], minor_axis_line[2], minor_axis_line[3], (0,0,255))

#         # enclosing circle
#         enclosing_circle = a.enclosing_circle()
#         img.draw_circle(enclosing_circle[0], enclosing_circle[1], enclosing_circle[2], (255,0,0))

#         # enclosing ellipse
#         enclosed_ellipse = a.enclosed_ellipse()
#         img.draw_ellipse(enclosed_ellipse[0], enclosed_ellipse[1], enclosed_ellipse[2], enclosed_ellipse[3], enclosed_ellipse[4], 0, 360, (0,0,255))

#         # hist(not use)
#         x_hist_bins = a.x_hist_bins()
#         y_hist_bins = a.y_hist_bins()

#     img.draw_rectangle(roi[0], roi[1], roi[2], roi[3], (0,255,0))
#     img.draw_string(roi[0] + 5, roi[1] + 5, "ROI", (0,255,0))
#     screen.show(img)
