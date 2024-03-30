from maix import camera, display, image
import math

cam = camera.Camera()
cam.open(width = 640, height = 480)

screen = display.Display(device = None, width = 640, height = 480)
screen.open()

roi = [160, 120, 320, 240]
merge_distance = 0
max_theta_diff = 15
while 1:
    img = cam.read()

    lines = img.find_line_segments(roi, merge_distance, max_theta_diff)
    for a in lines:
        img.draw_line(a.x1(), a.y1(), a.x2(), a.y2(), image.COLOR_RED, 2)
        img.draw_string(a.x2() + 5, a.y2() + 5, "len: " + str(a.length()), image.COLOR_RED)

        theta = a.theta()
        rho = a.rho()
        angle_in_radians = math.radians(theta)
        x = int(math.cos(angle_in_radians) * rho)
        y = int(math.sin(angle_in_radians) * rho)
        img.draw_line(0, 0, x, y, image.COLOR_GREEN, 2)
        img.draw_string(x, y, "theta: " + str(theta) + "," + "rho: " + str(rho), image.COLOR_GREEN)

    img.draw_rect(roi[0], roi[1], roi[2], roi[3], image.COLOR_GREEN)
    img.draw_string(roi[0] + 5, roi[1] + 5, "ROI", image.COLOR_GREEN)
    screen.show(img)
