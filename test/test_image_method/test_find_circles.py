from maix import camera, display, image

cam = camera.Camera()
cam.open(width = 640, height = 480)

screen = display.Display(device = None, width = 640, height = 480)
screen.open()

roi = [160, 120, 320, 240]
x_stride = 2
y_stride = 1
threshold = 3000
x_margin = 10
y_margin = 10
r_margin = 10
r_min = 20
r_max = 50
r_step = 2
while 1:
    img = cam.read()

    circles = img.find_circles(roi, x_stride, y_stride, threshold, x_margin, y_margin, r_margin, r_min, r_max, r_step)
    for a in circles:
        img.draw_circle(a.x(), a.y(), a.r(), image.COLOR_RED, 2)
        img.draw_string(a.x() + a.r() + 5, a.y() + a.r() + 5, "r: " + str(a.r()) + "magnitude: " + str(a.magnitude()), image.COLOR_RED)

    img.draw_rect(roi[0], roi[1], roi[2], roi[3], image.COLOR_GREEN)
    img.draw_string(roi[0] + 5, roi[1] + 5, "ROI", image.COLOR_GREEN)
    screen.show(img)
