from maix import camera, display, image, nn, app

cmap = image.CMap.TURBO
model = nn.DepthAnything(model="/root/models/depth_anything_v2_vits.mud", dual_buff = True)

cam = camera.Camera(model.input_width(), model.input_height(), model.input_format())
disp = display.Display()

while not app.need_exit():
    img = cam.read()
    res = model.get_depth_image(img, image.Fit.FIT_CONTAIN, cmap)
    if res:
        # show = image.Image(img.width() + res.width(), max(img.height(),res.height()), model.input_format())
        # show.draw_image(0, 0, img)
        # show.draw_image(img.width(), 0, res)
        # disp.show(show)
        disp.show(res)
