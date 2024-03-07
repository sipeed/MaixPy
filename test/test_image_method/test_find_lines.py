from maix import camera, display, image
import math

cam = camera.Camera()
cam.open(width = 640, height = 480)

screen = display.Display(device = None, width = 640, height = 480)
screen.open()

roi = [160, 120, 320, 240]                  # ROI
x_stride = 2
y_stride = 1
threshold = 2000
theta_margin = 30
rho_margin = 30

while 1:
    img = cam.read()

    lines = img.find_lines(roi, x_stride, y_stride, threshold, theta_margin, rho_margin)
    for a in lines:
        img.draw_line(a.x1(), a.y1(), a.x2(), a.y2(), image.COLOR_RED, 2)

        theta = a.theta()
        rho = a.rho()
        angle_in_radians = math.radians(theta)
        x = int(math.cos(angle_in_radians) * rho)
        y = int(math.sin(angle_in_radians) * rho)
        img.draw_line(0, 0, x, y, image.COLOR_GREEN, 2)
        img.draw_text(x, y, "theta: " + str(theta) + "," + "rho: " + str(rho), image.COLOR_GREEN)

    img.draw_rect(roi[0], roi[1], roi[2], roi[3], image.COLOR_GREEN)
    img.draw_text(roi[0] + 5, roi[1] + 5, "ROI", image.COLOR_GREEN)
    screen.show(img)
