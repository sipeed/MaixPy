from maix import camera, display, app, time, image

cam = camera.Camera(320, 224)
disp = display.Display()
detector = image.QRCodeDetector()
while not app.need_exit():
    img = cam.read()

    t = time.ticks_ms()
    qrcodes = detector.detect(img)
    t2 = time.ticks_ms()
    print(f"detect use {t2 - t} ms, fps:{1000 / (t2 - t)}")
    for q in qrcodes:
        corners = q.corners()
        for i in range(4):
            img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_RED)
        img.draw_string(0, 0, "payload: " + q.payload(), image.COLOR_BLUE)

    disp.show(img)

