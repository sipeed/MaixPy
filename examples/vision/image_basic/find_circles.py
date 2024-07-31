from maix import camera, display, image, app

cam = camera.Camera(320, 240)
disp = display.Display()

while not app.need_exit():
    img = cam.read()

    circles = img.find_circles(threshold = 3000)
    for a in circles:
        img.draw_circle(a.x(), a.y(), a.r(), image.COLOR_RED, 2)
        img.draw_string(a.x() + a.r() + 5, a.y() + a.r() + 5, "r: " + str(a.r()) + "magnitude: " + str(a.magnitude()), image.COLOR_RED)

    disp.show(img)

