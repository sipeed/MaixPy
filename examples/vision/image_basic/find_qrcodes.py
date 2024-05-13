from maix import camera, display, image

cam = camera.Camera(320, 240)
disp = display.Display()

while 1:
    img = cam.read()
    qrcodes = img.find_qrcodes()
    for q in qrcodes:
        corners = q.corners()
        for i in range(4):
            img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_RED)
        img.draw_string(0, 0, "payload: " + q.payload(), image.COLOR_BLUE)

    disp.show(img)
