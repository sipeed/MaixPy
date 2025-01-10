from maix import camera, display, image, nn, app


detect_conf_th = 0.5
detect_iou_th = 0.45
landmarks_conf_th = 0.5
landmarks_abs = True
landmarks_rel = False
max_face_num = 2
detector = nn.YOLOv8(model="/root/models/yolov8n_face.mud", dual_buff = False)
landmarks_detector = nn.FaceLandmarks(model="/root/models/face_landmarks.mud")

cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
disp = display.Display()

while not app.need_exit():
    img = cam.read()
    results = []
    objs = detector.detect(img, conf_th = detect_conf_th, iou_th = detect_iou_th, sort = 1)
    count = 0
    for obj in objs:
        img_std = landmarks_detector.crop_image(img, obj.x, obj.y, obj.w, obj.h, obj.points)
        if img_std:
            res = landmarks_detector.detect(img_std, landmarks_conf_th, landmarks_abs, landmarks_rel)
            if res and res.valid:
                results.append(res)
        count += 1
        if max_face_num > 0 and count >= max_face_num:
            break
    for res in results:
        landmarks_detector.draw_face(img, res.points, landmarks_detector.landmarks_num, res.points_z)
    disp.show(img)

