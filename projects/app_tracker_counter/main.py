from maix import nn, display, camera, app, time, image, tracker, touchscreen, sys

colors = [
    [255, 0, 0],       # 红色
    [0, 255, 0],       # 绿色
    [0, 0, 255],       # 蓝色
    [255, 255, 0],     # 黄色
    [0, 255, 255],     # 青色
    [255, 0, 255],     # 品红色
    [128, 0, 0],       # 深红色
    [0, 128, 0],       # 深绿色
    [0, 0, 128],       # 深蓝色
    [128, 128, 0],     # 橄榄色
    [0, 128, 128],     # 深青色
    [128, 0, 128],     # 紫色
    [255, 128, 0],     # 橙色
    [255, 0, 128],     # 玫瑰色
    [128, 255, 0],     # 黄绿色
    [0, 255, 128],     # 蓝绿色
    [128, 0, 255],     # 紫罗兰色
    [0, 128, 255],     # 天蓝色
    [255, 128, 128],   # 浅红色
    [128, 255, 128],   # 浅绿色
    [128, 128, 255],   # 浅蓝色
    [255, 255, 128],   # 浅黄色
    [128, 255, 255],   # 浅青色
    [255, 128, 255],   # 浅品红色
    [64, 0, 0],        # 暗红色
    [0, 64, 0],        # 暗绿色
    [0, 0, 64],        # 暗蓝色
    [64, 64, 0],       # 暗橄榄色
    [0, 64, 64],       # 暗青色
    [64, 0, 64],       # 暗紫色
    [255, 64, 0],      # 暗橙色
    [255, 0, 64],      # 暗玫瑰色
    [64, 255, 0],      # 暗黄绿色
    [0, 255, 64],      # 暗蓝绿色
    [64, 0, 255],      # 暗紫罗兰色
    [0, 64, 255],      # 暗天蓝色
    [255, 64, 64],     # 暗浅红色
    [64, 255, 64],     # 暗浅绿色
    [64, 64, 255],     # 暗浅蓝色
    [255, 255, 64],    # 暗浅黄色
    [64, 255, 255],    # 暗浅青色
    [255, 64, 255],    # 暗浅品红色
    [192, 192, 192],   # 银色
    [128, 128, 128],   # 灰色
    [64, 64, 64],      # 深灰色
    [255, 255, 255]    # 白色
]

def draw_yolo_results(img, objs, valid_class_id, font_scale, font_thickness, str_h):
    for obj in objs:
        if len(valid_class_id) > 0 and obj.class_id not in valid_class_id:
            continue
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color = image.COLOR_GRAY, thickness=font_thickness)
        msg = f'{detector.labels[obj.class_id]}: {obj.score:.2f}'
        img.draw_string(obj.x, obj.y + obj.h - str_h, msg, color = image.COLOR_GRAY, scale = font_scale, thickness = font_thickness)

def yolo_objs_to_tracker_objs(objs, valid_class_id):
    new = []
    for obj in objs:
        if len(valid_class_id) > 0 and obj.class_id not in valid_class_id:
            continue
        new.append(tracker.Object(obj.x, obj.y, obj.w, obj.h, obj.class_id, obj.score))
    return new

def show_tracks(img : image.Image, tracks, font_scale, font_thickness, str_h, start_y):
    valid = 0
    for track in tracks:
        if track.lost:
            continue
        valid += 1
        color = colors[track.id % len(colors)]
        color = image.Color.from_rgb(color[0], color[1], color[2])
        obj = track.history[-1]
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color, thickness=font_thickness)
        img.draw_string(obj.x, obj.y, f"{track.id} {track.score:.1f}", color, scale=font_scale, thickness=font_thickness)
        for i in range(1, len(track.history)):
            o = track.history[i]
            last_o = track.history[i - 1]
            img.draw_line(last_o.x + last_o.w // 2, last_o.y + last_o.h // 2, o.x + o.w // 2, o.y + o.h // 2, color=color, thickness=font_thickness)
    img.draw_string(2, start_y, f'valid: {valid}, total: {len(tracks)}', image.COLOR_RED, scale=font_scale, thickness=font_thickness)

def obj_in_roi(obj, roi):
    x = obj.x + obj.w // 2
    y = obj.y + obj.h // 2
    if x >= roi[0] and x <= roi[0] + roi[2]:
        if y < roi[1]:
            return -1
        if y > roi[1] + roi[3]:
            return 1
        return 0
    return None

def count_tracks(img, count_roi, tracks, count, down_track_ids, font_scale, font_thickness, str_h):
    # calculate object from up down, change code according to your application
    img.draw_rect(count_roi[0], count_roi[1], count_roi[2], count_roi[3], image.COLOR_YELLOW, thickness=2)
    # we assume: object latest center pos below roi and history pos in roi, it crossed roi from up to below.
    for track in tracks:
        if track.lost:
            continue
        obj = track.history[-1]
        ret = obj_in_roi(obj, count_roi)
        if ret is None:
            continue
        if ret > 0 and track.id not in down_track_ids:
            # find if last positions in roi
            for o in track.history[::-1][1:]:
                if obj_in_roi(o, count_roi) == 0:
                    count += 1
                    down_track_ids.append(track.id)
                    break
    img.draw_string(0, img.height() - str_h, f"up down: {count}", color=image.COLOR_RED, scale=font_scale, thickness=font_thickness)
    if len(down_track_ids) > 500: # remove some history we not use
        down_track_ids = down_track_ids[300:]
    return count, down_track_ids

def is_in_button(x, y, btn_pos):
    return x > btn_pos[0] and x < btn_pos[0] + btn_pos[2] and y > btn_pos[1] and y < btn_pos[1] + btn_pos[3]

def get_back_btn_img(width):
    ret_width = int(width * 0.1)
    img_back = image.load("/maixapp/share/icon/ret.png")
    w, h = (ret_width, img_back.height() * ret_width // img_back.width())
    if w % 2 != 0:
        w += 1
    if h % 2 != 0:
        h += 1
    img_back = img_back.resize(w, h)
    return img_back

def main(disp):
    # configs
    conf_threshold = 0.3       # detect threshold
    iou_threshold = 0.45       # detect iou threshold
    max_lost_buff_time = 120   # the frames for keep lost tracks.
    track_thresh = 0.4         # tracking confidence threshold.
    high_thresh = 0.6          # threshold to add to new track.
    match_thresh = 0.8         # matching threshold for tracking, e.g. one object in two frame iou < match_thresh we think they are the same obj.
    max_history_num = 10       # max tack's position history length.
    show_detect = False        # show detect
    valid_class_id = [0]       # we used classes index in detect model, empty means all class.

    # Any object detector, detect more stable the track will more stable
    if sys.device_name().lower() == "maixcam2":
        print("use yolo11s")
        detector = nn.YOLO11(model="/root/models/yolo11s.mud", dual_buff = True)
    else:
        print("use yolov5s")
        detector = nn.YOLOv5(model="/root/models/yolov5s.mud", dual_buff = True)
        # detector = nn.YOLOv8(model="/root/models/yolov8n.mud", dual_buff = True)

    cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
    tracker0 = tracker.ByteTracker(max_lost_buff_time, track_thresh, high_thresh, match_thresh, max_history_num)

    # back button
    img_back = get_back_btn_img(cam.width())
    back_rect = [0, 0, img_back.width(), img_back.height()]
    ts = touchscreen.TouchScreen()
    back_rect_disp = image.resize_map_pos(cam.width(), cam.height(), disp.width(), disp.height(), image.Fit.FIT_CONTAIN, back_rect[0], back_rect[1], back_rect[2], back_rect[3])

    font_scale = 2 if cam.height() >= 480 else 1.2
    font_thickness = 2 if cam.height() >= 480 else 1
    str_size = image.string_size("A", scale=font_scale, thickness=font_thickness)
    str_w = str_size.width()
    str_h = str_size.height()

    # counter
    count_roi = [0, cam.height() - cam.height() // 2, cam.width(), cam.height() // 9]
    up_down_count = 0
    down_track_ids = []

    while not app.need_exit():
        img = cam.read()
        objs = detector.detect(img, conf_th = conf_threshold, iou_th = iou_threshold)
        if show_detect:
            draw_yolo_results(img, objs, valid_class_id, font_scale, font_thickness, str_h)
        objs = yolo_objs_to_tracker_objs(objs, valid_class_id)
        tracks = tracker0.update(objs)
        show_tracks(img, tracks, font_scale, font_thickness, str_h, img_back.height() + font_thickness)
        up_down_count, down_track_ids = count_tracks(img, count_roi, tracks, up_down_count, down_track_ids, font_scale, font_thickness, str_h)
        img.draw_image(0, 0, img_back)
        disp.show(img)

        x, y, preesed = ts.read()
        if is_in_button(x, y, back_rect_disp):
            app.set_exit_flag(True)


disp = display.Display()
try:
    main(disp)
except Exception:
    import traceback
    msg = traceback.format_exc()
    img = image.Image(disp.width(), disp.height(), bg=image.COLOR_BLACK)
    img.draw_string(0, 0, msg, image.COLOR_WHITE)
    disp.show(img)
    while not app.need_exit():
        time.sleep_ms(100)
