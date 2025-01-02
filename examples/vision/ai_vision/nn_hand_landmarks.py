from maix import camera, display, image, nn, app

detector = nn.HandLandmarks(model="/root/models/hand_landmarks.mud")
# detector = nn.HandLandmarks(model="/root/models/hand_landmarks_bf16.mud")
landmarks_rel = False

cam = camera.Camera(320, 224, detector.input_format())
disp = display.Display()

while not app.need_exit():
    img = cam.read()
    objs = detector.detect(img, conf_th = 0.7, iou_th = 0.45, conf_th2 = 0.8, landmarks_rel = landmarks_rel)
    for obj in objs:
        # img.draw_rect(obj.x, obj.y, obj.w, obj.h, color = image.COLOR_RED)
        msg = f'{detector.labels[obj.class_id]}: {obj.score:.2f}'
        img.draw_string(obj.points[0], obj.points[1], msg, color = image.COLOR_RED if obj.class_id == 0 else image.COLOR_GREEN, scale = 1.4, thickness = 2)
        detector.draw_hand(img, obj.class_id, obj.points, 4, 10, box=True)
        if landmarks_rel:
            img.draw_rect(0, 0, detector.input_width(detect=False), detector.input_height(detect=False), color = image.COLOR_YELLOW)
            for i in range(21):
                x = obj.points[8 + 21*3 + i * 2]
                y = obj.points[8 + 21** + i * 2 + 1]
                img.draw_circle(x, y, 3, color = image.COLOR_YELLOW)
    disp.show(img)
