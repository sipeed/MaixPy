#!/usr/bin/env python3
"""
MaixPy uses nn.YOLO26Depth for real-time monocular depth estimation.  
Currently, it only supports the MaixCam2 platform.
"""

from maix import sys, app, camera, display, time, nn, image

if sys.device_name().lower() != "maixcam2":
    print("This example only supports the MaixCam2 platform.")

model = nn.YOLO26Depth("/root/models/yolo26n_depth_640x480.mud", dual_buff=True)
print(f"model input: {model.input_width()}x{model.input_height()} {model.input_format()}")

cam = camera.Camera(model.input_width(), model.input_height(), model.input_format())
disp = display.Display()
w = cam.width()
h = cam.height()
x = cam.width()//2
y = cam.height()//2

while not app.need_exit():
    img = cam.read()
    if img is None:
        continue

    r = model.get_depth(img)
    if r:
        heatmap = model.depth_to_image(r, img.width(), img.height())
        if heatmap:
            distance = model.get_distance(r, x, y, w, h)
            heatmap.draw_circle(x, y, 5, image.COLOR_BLACK, -1)
            heatmap.draw_string(x + 5, y, f"{distance:.2} m", image.COLOR_BLACK)
            disp.show(heatmap)
    else:
        time.sleep_ms(30)