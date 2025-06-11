from maix import camera, display, image, nn, app

cmap = image.CMap.TURBO
model = nn.DepthAnything(model="/root/models/depth_anything_v2_vits.mud", dual_buff = True)

cam = camera.Camera(model.input_width(), model.input_height(), model.input_format())
disp = display.Display()

while not app.need_exit():
    img = cam.read()
    res = model.get_depth_image(img, image.Fit.FIT_CONTAIN, cmap)
    if res:
        disp.show(res)
