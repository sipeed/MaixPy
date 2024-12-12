from maix import camera, display, image, nn, app, time

detector = nn.YOLO11(model="/root/models/yolo11n_seg.mud", dual_buff = True)

cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
disp = display.Display()

while not app.need_exit():
    img = cam.read()
    objs = detector.detect(img, conf_th = 0.5, iou_th = 0.45)
    for obj in objs:
        # img.draw_image(obj.x, obj.y, obj.seg_mask)
        detector.draw_seg_mask(img, obj.x, obj.y, obj.seg_mask, threshold=127)
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color = image.COLOR_RED)
        msg = f'{detector.labels[obj.class_id]}: {obj.score:.2f}'
        img.draw_string(obj.x, obj.y, msg, color = image.COLOR_RED)
    disp.show(img)
