from maix import camera, display, image
import math

cam = camera.Camera(320, 240)
disp = display.Display()

threshold = 2000

while 1:
    img = cam.read()

    lines = img.find_lines(threshold=2000)
    for a in lines:
        img.draw_line(a.x1(), a.y1(), a.x2(), a.y2(), image.COLOR_RED, 2)
        theta = a.theta()
        rho = a.rho()
        angle_in_radians = math.radians(theta)
        x = int(math.cos(angle_in_radians) * rho)
        y = int(math.sin(angle_in_radians) * rho)
        img.draw_line(0, 0, x, y, image.COLOR_GREEN, 2)
        img.draw_string(x, y, "theta: " + str(theta) + "," + "rho: " + str(rho), image.COLOR_GREEN)

    disp.show(img)
