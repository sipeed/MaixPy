from maix import camera, display, image, nn, app, time, hid

SHOW_IMG = True
DEBUG_MODE = False
trans_img_quality = 51 # 51 ~ 99
# model_path = "/root/models/yolo11n_pose_224.mud"
model_path = "/root/models/yolo11n_pose.mud"
KEY_POSE_LEFT = 80
KEY_POSE_RIGHT = 79
KEY_POSE_UP = 22     # S
KEY_POSE_DOWN = 81
KEY_POSE_ATTACK = 29 # Z
# KEY_POSE_ATTACK = 4 # A

if DEBUG_MODE:
    SHOW_IMG = True

class PoseRecognizer:
    POSE_NONE = 0
    POSE_LEFT = 1
    POSE_RIGHT = 2
    POSE_UP = 3
    POSE_DOWN = 4
    POSE_ATTACK = 5
    str_pose = {
        POSE_NONE: "No Pose",
        POSE_LEFT: "<<<",
        POSE_RIGHT: ">>>",
        POSE_UP: "^^",
        POSE_DOWN: "__",
        POSE_ATTACK: "@@",
    }

    def __init__(self, img_w, img_h, th_left_right = 0.15, down_line = 0.7, min_shoulder_len = 20, th_up = 0.2, up_detect_rest_interval = 0.2, y_debouncee_pix = 5, y_high_freq_th = 500, jump_pix_th = 20):
        '''
            th_left_right: 如果肩膀和胯部中心的水平位置距离和两肩的距离的比值小于这个值，则认为人直立
            y_high_freq_th: 过滤高频振动阈值，每秒移动的像素数量超过这个值就过滤掉
            jump_pix_th: 往上移动多少算一次跳跃
        '''
        self.th_left_right = th_left_right
        self.img_w = img_w
        self.img_h = img_h
        self.min_shoulder_len = min_shoulder_len
        self.down_line = int(self.img_h * down_line)
        self.str_h = image.string_size("aA!~@#").height()
        self.str_h_x2 = image.string_size("aA!~@#", scale=2).height()
        self.up_detect_rest_interval = up_detect_rest_interval
        self.th_up = self.img_h * th_up
        self.up_count = 0
        self.last_up_time = 0
        self.last_down_time = 0
        self.y_points = [] #[[time, position], ]
        self.y_dir = 0 # 0: none, 1: up, 2: down
        self.y_debouncee_pix = y_debouncee_pix
        self.y_high_freq_th = y_high_freq_th
        self.jump_pix_th = jump_pix_th
        self.last_jump_time = 0
        self.last_jump_line = 0
        self.last_steady_time = 0
        self.steady_line = 0
        self.last_steady_line = 0
        self.falling = False

    def run(self, img : image.Image, obj : nn.Object):
        '''
            Return:
                valid(bool type), poses(list type)
        '''
        res = []
        # nose_x = obj.points[0]
        shoulder_left = [obj.points[10], obj.points[11]]
        shoulder_right = [obj.points[12], obj.points[13]]
        elbow_left = [obj.points[14], obj.points[15]]
        elbow_right = [obj.points[16], obj.points[17]]
        wrist_left = [obj.points[18], obj.points[19]]
        wrist_right = [obj.points[20], obj.points[21]]
        hip_left = [obj.points[22], obj.points[23]]
        hip_right = [obj.points[24], obj.points[25]]
        shoulder_len = abs(shoulder_left[0] - shoulder_right[0])
        if (-1 in [shoulder_left[0], shoulder_right[0], hip_left[0], hip_right[0]]) or shoulder_len < self.min_shoulder_len:
            img.draw_string(6, 4, "Invalid Pose", image.COLOR_RED, scale=2, thickness=-2)
            return False, res
        shoulder_mid = [(shoulder_left[0] + shoulder_right[0]) * 0.5, (shoulder_left[1] + shoulder_right[1]) * 0.5]
        hip_mid = [(hip_left[0] + hip_right[0]) * 0.5, (hip_left[1] + hip_right[1]) * 0.5]
        mid_x, mid_y = [(hip_mid[0] + shoulder_mid[0]) * 0.5, (hip_mid[1] + shoulder_mid[1]) * 0.5]
        if SHOW_IMG:
            img.draw_circle(int(mid_x), int(mid_y), 5, image.COLOR_WHITE, 4)
            # img.draw_circle(int(shoulder_mid[0]), int(shoulder_mid[1]), 5, image.COLOR_WHITE, 2)
            # img.draw_circle(int(hip_mid[0]), int(hip_mid[1]), 5, image.COLOR_WHITE, 2)

        now = time.ticks_ms()
        if len(self.y_points) == 0: # first time
            self.y_points.append([now, mid_y])
        else:
            delta = mid_y - self.y_points[-1][1]
            if abs(delta * 1000 / (now - self.y_points[-1][0])) > self.y_high_freq_th: # 过滤高频
                print("!!!!! high freq")
                pass
            else:
                if mid_y > self.down_line: # 蹲下
                    res.append(self.POSE_DOWN)
                    self.last_down_time = now
                    self.y_points = [[now, mid_y]]
                else:
                    self.y_points.append([now, mid_y])
                self.y_points, up_height, new_jump = self.finde_up(self.y_points, self.jump_pix_th)
                if up_height > 0:
                    res.append(self.POSE_UP)
        if DEBUG_MODE:
            for i, (t, y) in enumerate(self.y_points):
                img.draw_circle(i, int(y), 1, image.COLOR_ORANGE)

        v = (shoulder_mid[0] - hip_mid[0]) / shoulder_len
        if v > self.th_left_right:
            res.append(self.POSE_RIGHT)
        elif v < -self.th_left_right:
            res.append(self.POSE_LEFT)
        # 举手
        if wrist_left[1] < shoulder_left[1] or wrist_right[1] < shoulder_right[1]:
            res.append(self.POSE_ATTACK)
        return True, res

    def finde_up(self, poinsts, threshold):
        '''
            Return (points, jump_height, new_jump), if jump detected(height >= threshold) jump_height > 0, or up_height is 0
        '''
        last_y = self.img_h
        y_top = last_y
        new_start_idx = 0
        new_jump = False
        jump_height = 0
        now = time.ticks_ms()
        for i, (t, y) in enumerate(self.y_points):
            d = y - last_y
            if abs(d) < self.y_debouncee_pix: # 检查不动
                if self.last_steady_time == 0:
                    self.last_steady_time = t
                if now - self.last_steady_time > 4000: # steady timess
                    # print("time out")
                    new_start_idx = i
                    last_y = y
                    y_top = last_y
                    self.steady_line = y
                    self.last_jump_line = 0
                    self.last_jump_time = 0
                    self.last_steady_time = 0
                    continue
            else:
                self.last_steady_time = 0

            if self.last_jump_line > 0 and (y < self.steady_line - self.y_debouncee_pix): # 等待回到中心线
                jump_height = self.last_jump_line - y
                last_y = y
                continue

            if d <= self.y_debouncee_pix: # 认为向上运动
                if y < y_top:
                    y_top = y
                    if (self.last_jump_time != self.y_points[0][0]) and (self.steady_line - y_top > threshold):
                        self.last_jump_time = t
                        new_start_idx = i
                        self.up_count += 1
                        print("new jump:", self.up_count)
                        new_jump = True
                        self.last_jump_line = self.steady_line
                jump_height = self.last_jump_line - y
            else: # 向下运动
                y_top = y
                print("down")
                new_start_idx = i + 1
                self.last_jump_time = 0
                self.last_jump_line = 0
                jump_height = 0
                self.last_steady_time = 0
            last_y = y
        # print(jump_height)
        return poinsts[new_start_idx:], jump_height, new_jump


    def draw_pose_info(self, img : image.Image, poses : list[int]):
        img.draw_line(50, self.down_line, self.img_w - 50, self.down_line, color=image.COLOR_WHITE, thickness=2)
        img.draw_line(10, int(self.steady_line), self.img_w - 10, int(self.steady_line), color=image.COLOR_RED, thickness=1)
        # img.draw_line(0, int(self.steady_line) + self.y_debouncee_pix, self.img_w - 2, int(self.steady_line) + self.y_debouncee_pix, color=image.COLOR_WHITE, thickness=1)
        # img.draw_line(0, int(self.steady_line) - self.y_debouncee_pix, self.img_w - 2, int(self.steady_line) - self.y_debouncee_pix, color=image.COLOR_WHITE, thickness=1)
        # img.draw_line(0, int(self.steady_line) - self.jump_pix_th, self.img_w - 2, int(self.steady_line) - self.jump_pix_th, color=image.COLOR_GREEN, thickness=1)
        # msg = f"Jump: {self.up_count} "
        # for pose in poses:
        #     msg += f'{self.str_pose[pose]} '
        # img.draw_string(4, self.img_h - self.str_h_x2 - 4, msg, image.COLOR_PURPLE, scale=2, thickness=-5)
        # img.draw_string(4, self.img_h - self.str_h_x2 - 4, msg, image.COLOR_WHITE, scale=2, thickness=-3)
        if self.steady_line == 0:
            img.draw_string(6, 40, "Stand Still !", image.COLOR_RED, scale=2, thickness=-2)
    

def send_keys(poses, keyboard, keys):
    cmd = [0, 0]
    for pose in poses:
        key_id = keys[pose]
        cmd.append(key_id)
    if len(cmd) < 8:
        cmd.extend([0] * (8 - len(cmd)))
    keyboard.write(cmd)


class HID_NOT_READY(Exception):
    pass

def main(disp):
    keys = {
        PoseRecognizer.POSE_LEFT: KEY_POSE_LEFT,
        PoseRecognizer.POSE_RIGHT: KEY_POSE_RIGHT,
        PoseRecognizer.POSE_UP: KEY_POSE_UP,
        PoseRecognizer.POSE_DOWN: KEY_POSE_DOWN,
        PoseRecognizer.POSE_ATTACK: KEY_POSE_ATTACK
    }

    detector = nn.YOLO11(model=model_path, dual_buff = True)

    cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
    cam.hmirror(1)
    recognizer = PoseRecognizer(cam.width(), cam.height())

    try:
        keyboard = hid.Hid(hid.DeviceType.DEVICE_KEYBOARD)
    except Exception as e:
        print(e)
        raise HID_NOT_READY()

    find_flag = False
    while not app.need_exit():
        img = cam.read()
        objs = detector.detect(img, conf_th = 0.5, iou_th = 0.45, keypoint_th = 0.5)
        if len(objs) > 0:
            find_flag = True
            max_s = 0
            max_idx = 0
            for i, obj in enumerate(objs):
                s = obj.w * obj.h 
                if s > max_s:
                    max_s = s
                    max_idx = i
            for i, obj in enumerate(objs):
                if max_idx == i:
                    valid, poses = recognizer.run(img, obj)
                    if valid:
                        color = image.COLOR_GREEN
                        send_keys(poses, keyboard, keys)
                    else:
                        color = image.COLOR_RED
                    if SHOW_IMG:
                        # img.draw_rect(obj.x, obj.y, obj.w, obj.h, color = color)
                        detector.draw_pose(img, obj.points, 4, color)
                        recognizer.draw_pose_info(img, poses)
                # else:
                #     color = image.COLOR_YELLOW
                #     detector.draw_pose(img, obj.points, 2, color, body=False)
        else:
            if find_flag:
                send_keys([], keyboard, keys)
                find_flag = False
        if SHOW_IMG:
            disp.show(img)
            # display.send_to_maixvision(img)

if __name__ == '__main__':
    screen = display.Display()
    # set send to maixvision quality
    try:
        display.set_trans_image_quality(trans_img_quality)
    except Exception:
        pass
    try:
        main(screen)
    except Exception as e:
        if type(e) == HID_NOT_READY:
            msg = 'Set USB HID mode first:\n\n'
            msg += 'Settings -> USB Settings -> HID Keyboard, click Confirm.\n\n'
            msg += 'Or run examples/tools/maixcam_switch_usb_mode.py to enable the HID Keyboard.'
            scale = 1.2
        else:
            import traceback
            msg = traceback.format_exc()
            print(msg)
            scale = 0.6
        msg += "\n\npress button to exit"
        img = image.Image(screen.width(), screen.height())
        img.draw_string(2, 2, msg, image.COLOR_WHITE, font="hershey_complex_small", scale=scale)
        screen.show(img)
        while not app.need_exit():
            time.sleep(0.2)
