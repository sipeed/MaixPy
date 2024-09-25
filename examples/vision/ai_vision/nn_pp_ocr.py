from maix import camera, display, image, nn, app

model = "/root/models/pp_ocr.mud"
ocr = nn.PP_OCR(model)

cam = camera.Camera(ocr.input_width(), ocr.input_height(), ocr.input_format())
disp = display.Display()

image.load_font("ppocr", "/maixapp/share/font/ppocr_keys_v1.ttf", size = 20)
image.set_default_font("ppocr")

while not app.need_exit():
    img = cam.read()
    objs = ocr.detect(img)
    for obj in objs:
        points = obj.box.to_list()
        img.draw_keypoints(points, image.COLOR_RED, 4, -1, 1)
        img.draw_string(obj.box.x4, obj.box.y4, obj.char_str(), image.COLOR_RED)
    disp.show(img)
