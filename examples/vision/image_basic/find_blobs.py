from maix import camera, display, image

cam = camera.Camera(320, 240)
disp = display.Display()

area_threshold = 1000
pixels_threshold = 1000
# thresholds = [[0, 80, 40, 80, 10, 80]]        # red
thresholds = [[0, 80, -120, -10, 0, 30]]        # green
# thresholds = [[0, 80, 30, 100, -120, -60]]    # blue
while 1:
    img = cam.read()

    blobs = img.find_blobs(thresholds, area_threshold = 1000, pixels_threshold = 1000)
    for b in blobs:
        corners = b.corners()
        for i in range(4):
            img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_RED)

    disp.show(img)
