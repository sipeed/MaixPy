from maix import nn, display, camera, app, time, image, tracker

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

def draw_yolo_results(img, objs, valid_class_id):
    msg_h = image.string_size("1!aA,</?").height()
    for obj in objs:
        if obj.class_id not in valid_class_id:
            continue
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color = image.COLOR_GRAY)
        msg = f'{detector.labels[obj.class_id]}: {obj.score:.2f}'
        img.draw_string(obj.x, obj.y + obj.h - msg_h, msg, color = image.COLOR_GRAY)

def yolo_objs_to_tracker_objs(objs, valid_class_id):
    new = []
    for obj in objs:
        if obj.class_id not in valid_class_id:
            continue
        new.append(tracker.Object(obj.x, obj.y, obj.w, obj.h, obj.class_id, obj.score))
    return new

def show_tracks(img : image.Image, tracks):
    valid = 0
    for track in tracks:
        if track.lost:
            continue
        valid += 1
        color = colors[track.id % len(colors)]
        color = image.Color.from_rgb(color[0], color[1], color[2])
        obj = track.history[-1]
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color, thickness=2)
        img.draw_string(obj.x, obj.y, f"{track.id} {track.score:.1f}", color, scale=1.3)
        for obj in track.history:
            img.draw_circle(obj.x + obj.w // 2, obj.y + obj.h // 2, 1, color, -1)
    img.draw_string(2, 2, f'valid: {valid}, total: {len(tracks)}', image.COLOR_RED)

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

# configs
conf_threshold = 0.3       # detect threshold
iou_threshold = 0.45       # detect iou threshold
max_lost_buff_time = 120   # the frames for keep lost tracks.
track_thresh = 0.4         # tracking confidence threshold.
high_thresh = 0.6          # threshold to add to new track.
match_thresh = 0.8         # matching threshold for tracking, e.g. one object in two frame iou < match_thresh we think they are the same obj.
max_history_num = 5       # max tack's position history length.
show_detect = False        # show detect
valid_class_id = [0]       # we used classes index in detect model。

# Any object detector, detect more stable the track will more stable
detector = nn.YOLOv5(model="/root/models/yolov5s.mud", dual_buff = True)
# detector = nn.YOLOv8(model="/root/models/yolov8n.mud", dual_buff = True)

disp = display.Display()
cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
tracker0 = tracker.ByteTracker(max_lost_buff_time, track_thresh, high_thresh, match_thresh, max_history_num)

while not app.need_exit():
    img = cam.read()
    objs = detector.detect(img, conf_th = conf_threshold, iou_th = iou_threshold)
    if show_detect:
        draw_yolo_results(img, objs, valid_class_id)
    objs = yolo_objs_to_tracker_objs(objs, valid_class_id)
    tracks = tracker0.update(objs)
    show_tracks(img, tracks)
    disp.show(img)
