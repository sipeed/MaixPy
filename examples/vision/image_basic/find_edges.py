from maix import camera, display
from maix.image import EdgeDetector

cam = camera.Camera(320, 240)
disp = display.Display()

edge_type = EdgeDetector.EDGE_CANNY

while 1:
    img = cam.read()
    img.find_edges(edge_type, threshold=[50, 100])
    disp.show(img)
