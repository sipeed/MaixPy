from maix import camera, display, image

cam = camera.Camera()
cam.open(width = 640, height = 480)

screen = display.Display(device = None, width = 640, height = 480)
screen.open()

roi = [160, 120, 320, 240]
type = image.EdgeDetector.EDGE_CANNY
threshold = [100, 200]
while 1:
    img = cam.read()

    img.find_edges(type, roi, threshold)
    img.draw_rect(roi[0], roi[1], roi[2], roi[3], image.COLOR_GREEN)
    img.draw_text(roi[0] + 5, roi[1] + 5, "ROI", image.COLOR_GREEN)

    screen.show(img)
