from maix import camera, display, image
from maix.image import ApriltagFamilies

cam = camera.Camera(160, 120)
disp = display.Display()

families = ApriltagFamilies.TAG36H11

while 1:
    img = cam.read()

    apriltags = img.find_apriltags(families=ApriltagFamilies.TAG36H11)
    for a in apriltags:
        corners = a.corners()
        for i in range(4):
            img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_GREEN, 2)

    disp.show(img)
