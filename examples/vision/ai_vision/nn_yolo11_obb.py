from maix import camera, display, image, nn, app

detector = nn.YOLO11(model="/root/models/yolo11n_obb.mud", dual_buff = True)

cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
disp = display.Display()

while not app.need_exit():
    img = cam.read()
    objs = detector.detect(img, conf_th = 0.5, iou_th = 0.45)
    for obj in objs:
        # img.draw_rect(obj.x, obj.y, obj.w, obj.h, color = image.COLOR_RED)
        points = obj.get_obb_points()
        msg = f'{detector.labels[obj.class_id]}: {obj.score:.2f}, {obj.angle * 180:.1f}'
        img.draw_string(points[0], points[1] - 4, msg, color = image.COLOR_RED)
        detector.draw_pose(img, points, 8 if detector.input_width() > 480 else 4, image.COLOR_RED, close=True)
    disp.show(img)
