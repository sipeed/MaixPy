from maix import hid, time, app, display, camera, image, sys, nn, touchscreen, key
import numpy as np
import math
from collections import deque

class Status:
    SELECT_PEOPLE = 0,
    RUN = 1,

class MovingAverageFilter:
    def __init__(self, window_size=5):
        self.window_size = window_size
        self.x_points = deque(maxlen=window_size)
        self.y_points = deque(maxlen=window_size)

    def update(self, x, y):
        self.x_points.append(x)
        self.y_points.append(y)

        if len(self.x_points) < self.window_size:
            return x, y

        filtered_x = np.mean(self.x_points).astype(int)
        filtered_y = np.mean(self.y_points).astype(int)

        return filtered_x, filtered_y

class Point:
    def __init__(self, x, y, filter = True):
        self.x = x
        self.y = y
        self.need_filter = filter
        if self.need_filter:
            self.filter = MovingAverageFilter()
    def update(self, x, y):
        if self.need_filter:
            self.x, self.y = self.filter.update(x, y)
        else:
            self.x = x
            self.y = y

class FingerPoint:
    x: int
    y: int
    def __init__(self, x, y):
        self.x = x
        self.y = y

class App:
    def __init__(self):
        self.disp = display.Display()
        display.set_trans_image_quality(19)
        self.ts = touchscreen.TouchScreen()
        if sys.device_id() in ["maixcam", "maixcam-pro"]:
            cam_w = 320
            cam_h = 240
            model_path = "/root/models/yolov8n_pose.mud"
            self.detector = nn.YOLOv8(model=model_path, dual_buff = True)
        else:
            cam_w = 640
            cam_h = 480
            model_path = "/root/models/yolov8n_pose.mud"
            self.detector = nn.YOLOv8(model="/root/models/yolov8n_pose.mud", dual_buff = False)
        self.cam = camera.Camera(cam_w, cam_h, fps=60)

        self.cam_roi = [0.1, 0.1, 0.9, 0.8]     # float, unit is percent
        self.dst_screen_roi = [0, 0, 1, 1]      # float, unit is percent
        self.invert_x = True
        self.invert_y = False
        self.select_people_need_mirror = False
        self.play_game_need_mirror = True
        self.cam.hmirror(self.select_people_need_mirror)
        try:
            # self.keyboard = hid.Hid(hid.DeviceType.DEVICE_KEYBOARD)
            # self.touchpad = hid.Hid(hid.DeviceType.DEVICE_TOUCHPAD)
            self.mouse = hid.Hid(hid.DeviceType.DEVICE_MOUSE)
            self.last_press_ms = time.ticks_ms()
        except Exception as e:
            print(e)
            print('The HID Device is not enabled')
            print('Try: Use the application Settings -> USB Settings -> HID MOUSE, then click Confirm, and restart the system.')
            print('You can also use examples/tools/maixcam_switch_usb_mode.py to enable the HID Mouse, then restart the system.')
            self.show_error_msg("The HID Mouse Device is not enabled")

        self.key_obj = key.Key(self.on_key)
        self.key_state = 0

        self.status = Status.SELECT_PEOPLE

    def on_key(self, key_id, state):
        '''
            this func called in a single thread
        '''
        # print(f"key: {key_id}, state: {state}") # key.c or key.State.KEY_RELEASED
        if state:
            self.key_state = state

    def show_error_msg(self, msg: str, block=True):
        img = image.Image(self.disp.width(), self.disp.height())
        img.clear()
        img.draw_string(0, 0, msg, image.COLOR_WHITE)
        self.disp.show(img)
        if block:
            while not app.need_exit():
                time.sleep_ms(100)


    def signed_angle_between_lines(self, A, B, C, D, in_degrees=True):
        """
        计算从直线AB到直线CD的有符号夹角
        
        Args:
            A, B: 第一条直线的两点
            C, D: 第二条直线的两点
            in_degrees: 是否返回角度值

        Returns:
            有符号夹角，正值表示逆时针旋转，负值表示顺时针旋转
        """
        # 计算两个向量的角度
        angle1 = math.atan2(B[1] - A[1], B[0] - A[0])
        angle2 = math.atan2(D[1] - C[1], D[0] - C[0])

        # 计算夹角（考虑2π周期）
        angle_diff = angle2 - angle1
        if angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        elif angle_diff < -math.pi:
            angle_diff += 2 * math.pi

        if in_degrees:
            return math.degrees(angle_diff)
        else:
            return angle_diff

    def get_finger_points(self, points, index) -> FingerPoint:
        return FingerPoint(points[8 + 3 * index], points[8 + 3 * index + 1])

    def cal_distance(self, p1, p2):
        return math.sqrt(math.pow((p2[0] - p1[0]), 2) + math.pow((p2[1] - p1[1]), 2))

    def touchpad_set(self, button, x_oft, y_oft, wheel_move):
        self.touchpad.write([button,
                        x_oft & 0xff, (x_oft >> 8) & 0xff,
                        y_oft & 0xff, (y_oft >> 8) & 0xff,
                        wheel_move])

    def press(self, method):
        if time.ticks_ms() - self.last_press_ms < 50:
            return
        oft = 150
        print('run', method)
        if method == 'left':
            self.mouse.write([1, -oft, 0, 0])
            time.sleep_ms(20)
            self.mouse.write([0, oft, 0, 0])
        elif method == 'right':
            self.mouse.write([1, oft, 0, 0])
            time.sleep_ms(20)
            self.mouse.write([0, -oft, 0, 0])
        elif method == 'up':
            self.mouse.write([1, 0, -oft, 0])
            time.sleep_ms(20)
            self.mouse.write([0, 0, oft, 0])
        elif method == 'down':
            self.mouse.write([1, 0, oft, 0])
            time.sleep_ms(20)
            self.mouse.write([0, 0, -oft, 0])
        else:
            pass
        self.last_press_ms = time.ticks_ms()

    def run(self):
        left_lower_limbs_point = Point(0, 0)
        right_lower_limbs_point = Point(0, 0)
        left_upper_limbs_point = Point(0, 0)
        right_upper_limbs_point = Point(0, 0)
        center_point = Point(0, 0)
        last_center_point = Point(0, 0, filter=False)

        upper_valid = False          # 跳完后才有效
        down_valid = False
        upper_limbs_base_degress = 90           # 初始上身肩膀的角度, 会在校准时被修改
        upper_limbs_offset_degress = 10         # 偏移角度, 肩膀旋转超过改角度时认为发生了旋转
        detect_roi = [0, 0, 0, 0]
        left_or_right_valid = False

        last_disp_ms = time.ticks_ms()
        up_max_y = self.cam.height() // 6 * 4
        down_min_y = self.cam.height() - self.cam.height() // 6
        pressing = False
        target = nn.Object()
        btn_str = "Select"
        font_size = image.string_size(btn_str)
        last_not_action_ms = time.ticks_ms()
        last_loop_ms = time.ticks_ms()
        def calibrate(final_obj, oft_x = 0, oft_y = 0, hmirror= False, without_limbs_degress = False):
            nonlocal left_lower_limbs_point
            nonlocal right_lower_limbs_point
            nonlocal left_upper_limbs_point
            nonlocal right_upper_limbs_point
            nonlocal center_point
            nonlocal up_max_y
            nonlocal down_min_y
            nonlocal upper_limbs_base_degress
            nonlocal detect_roi
            left_lower_limbs_point = Point(final_obj.points[2*11] + oft_x, final_obj.points[2*11+1] + oft_y)
            right_lower_limbs_point = Point(final_obj.points[2*12] + oft_x, final_obj.points[2*12+1] + oft_y)
            left_upper_limbs_point = Point(final_obj.points[2*5] + oft_x, final_obj.points[2*5+1] + oft_y)
            right_upper_limbs_point = Point(final_obj.points[2*6] + oft_x, final_obj.points[2*6+1] + oft_y)

            center_point = Point((left_lower_limbs_point.x + right_lower_limbs_point.x)//2, (left_lower_limbs_point.y + right_lower_limbs_point.y)//2)
            # 上肩和大腿的距离的比例作为跳跃和蹲下的上下限
            up_oft = abs(center_point.y - left_upper_limbs_point.y) // 8
            up_max_y = center_point.y - up_oft
            down_oft = abs(center_point.y - left_upper_limbs_point.y) // 6
            down_min_y = center_point.y + down_oft
            print('Config up max y', up_max_y, 'oft:', up_oft)
            print('Config down min y', down_min_y, 'oft:', down_oft)

            if not without_limbs_degress:
                upper_limbs_degress = self.signed_angle_between_lines([0,0], [0, 100],
                            [left_upper_limbs_point.x, left_upper_limbs_point.y], [right_upper_limbs_point.x, right_upper_limbs_point.y])
                if hmirror:
                    upper_limbs_base_degress = 180 - upper_limbs_degress    # 和检测时的摄像头镜像了
                else:
                    upper_limbs_base_degress = upper_limbs_degress
                print('Config upper_limbs_base_degress to', upper_limbs_base_degress)
            else:
                print('Do not config upper_limbs_base_degress')

            extra_width = int(final_obj.w * 0.4)
            if hmirror:
                detect_roi = [img.width() - (final_obj.x + oft_x) - final_obj.w - extra_width, 0, extra_width*2 + final_obj.w, final_obj.h * 3]
            else:
                detect_roi = [final_obj.x + oft_x - extra_width, 0, extra_width*2 + final_obj.w, final_obj.h * 3]
            detect_roi[0] = max(0, min(img.width()-1, detect_roi[0]))
            detect_roi[1] = max(0, min(img.height()-1, detect_roi[1]))
            detect_roi[2] = max(0, min(img.width(), detect_roi[2]))
            detect_roi[3] = max(0, min(img.height(), detect_roi[3]))
            print('Config detect roi to', detect_roi)

        while not app.need_exit():
            img = self.cam.read()
            touch_status = self.ts.read()
            if self.status == Status.SELECT_PEOPLE:
                big_objs = self.detector.detect(img, conf_th = 0.5, iou_th = 0.45, keypoint_th = 0.5)
                final_big_obj = None
                if len(big_objs) > 0:
                    final_big_obj = max(big_objs, key=lambda x : x.w * x.h)
                if touch_status[2]:  # Finger press detected
                    if not pressing:
                        target.x = touch_status[0]
                        target.y = touch_status[1]
                        print("Start select")
                    pressing = True
                else:
                    if pressing:  # Finger released, finalize selection
                        target.w = touch_status[0] - target.x
                        target.h = touch_status[1] - target.y
                        target.x = max(0, min(img.width()-1, target.x))
                        target.y = max(0, min(img.height()-1, target.y))
                        target.w = max(0, min(img.width(), target.w))
                        target.h = max(0, min(img.height(), target.h))
                        if target.w > 0 and target.h > 0:
                            print('crop:', target.x, target.y, target.w, target.h)
                            crop_img = img.crop(target.x, target.y, target.w, target.h)
                            objs = self.detector.detect(crop_img, conf_th = 0.5, iou_th = 0.45, keypoint_th = 0.5)
                            final_obj = None
                            if len(objs) > 0:
                                final_obj = max(objs, key=lambda x : x.w * x.h)
                            if final_obj:
                                crop_img.draw_rect(final_obj.x, final_obj.y, final_obj.w, final_obj.h, color = image.COLOR_GREEN)
                                self.detector.draw_pose(crop_img, final_obj.points, 8 if self.detector.input_width() > 480 else 4, image.COLOR_GREEN)
                                img.draw_image(0, 0, crop_img)

                                calibrate(final_obj, oft_x=target.x, oft_y=target.y, hmirror=self.select_people_need_mirror)
                                img.draw_line(0, up_max_y, img.width(), up_max_y, image.COLOR_RED, 2)
                                img.draw_line(0, down_min_y, img.width(), down_min_y, image.COLOR_RED, 2)
                                self.status = Status.RUN
                                self.cam.hmirror(self.play_game_need_mirror)
                                print('enter Status.RUN')
                            else:
                                print("Not found people")

                        else:
                            print(f"Rectangle invalid, x: {target.x}, y: {target.y}, w: {target.w}, h: {target.h}")
                    pressing = False

                if self.key_state:
                    self.key_state = 0
                    final_obj = final_big_obj
                    if final_obj:
                        self.detector.draw_pose(img, final_obj.points, 8 if self.detector.input_width() > 480 else 4, image.COLOR_GREEN)
                        calibrate(final_obj, hmirror=self.select_people_need_mirror)
                        img.draw_line(0, up_max_y, img.width(), up_max_y, image.COLOR_RED, 2)
                        img.draw_line(0, down_min_y, img.width(), down_min_y, image.COLOR_RED, 2)
                        self.status = Status.RUN
                        self.cam.hmirror(self.play_game_need_mirror)
                        print('enter Status.RUN')

                if final_big_obj:
                    img.draw_rect(final_big_obj.x, final_big_obj.y, final_big_obj.w, final_big_obj.h, color = image.COLOR_RED)
                    self.detector.draw_pose(img, final_big_obj.points, 8 if self.detector.input_width() > 480 else 4, image.COLOR_RED)

                if pressing:
                    img.draw_string(2, img.height() - font_size[1] * 2, "Select and release to complete", image.Color.from_rgb(255, 0, 0), 1.5)
                    img.draw_rect(target.x, target.y, touch_status[0] - target.x, touch_status[1] - target.y, image.Color.from_rgb(255, 0, 0), 3)
                else:
                    img.draw_string(2, img.height() - font_size[1] * 2, "Select target on screen", image.Color.from_rgb(255, 0, 0), 1.5)

                if time.ticks_ms() - last_disp_ms > 30:
                    # display.send_to_maixvision(img)
                    self.disp.show(img)
                    last_disp_ms = time.ticks_ms()
            else:
                if touch_status[2] or self.key_state:
                    self.key_state = 0
                    self.status = Status.SELECT_PEOPLE
                    self.cam.hmirror(self.select_people_need_mirror)
                    print('enter Status.SELECT_PEOPLE')
                    continue

                img.draw_rect(detect_roi[0], detect_roi[1], detect_roi[2], detect_roi[3], image.COLOR_GREEN, 2)
                new_img = img.copy()
                new_img.draw_rect(0, 0, (img.width() - detect_roi[2])//2, img.height(), image.COLOR_BLACK, -1)
                new_img.draw_rect(detect_roi[0] + detect_roi[2], 0, (img.width() - detect_roi[2])//2, img.height(), image.COLOR_BLACK, -1)
                objs = self.detector.detect(new_img, conf_th = 0.5, iou_th = 0.45, keypoint_th = 0.5)


                final_obj = None
                if len(objs) > 0:
                    final_obj = max(objs, key=lambda x : x.w * x.h)
                if final_obj \
                    and final_obj.points[2*11] != -1 and final_obj.points[2*11+1] != -1 \
                    and final_obj.points[2*12] != -1 and final_obj.points[2*12+1] != -1:
                    img.draw_rect(final_obj.x, final_obj.y, final_obj.w, final_obj.h, color = image.COLOR_RED)
                    self.detector.draw_pose(img, final_obj.points, 8 if self.detector.input_width() > 480 else 4, image.COLOR_RED)

                    left_lower_limbs_point.update(final_obj.points[2*11], final_obj.points[2*11+1])
                    right_lower_limbs_point.update(final_obj.points[2*12], final_obj.points[2*12+1])
                    left_upper_limbs_point.update(final_obj.points[2*5], final_obj.points[2*5+1])
                    right_upper_limbs_point.update(final_obj.points[2*6], final_obj.points[2*6+1])

                    upper_limbs_degress = self.signed_angle_between_lines([0,0], [0, 100],
                    [left_upper_limbs_point.x, left_upper_limbs_point.y], [right_upper_limbs_point.x, right_upper_limbs_point.y])
                    img.draw_string(0, 0, str(upper_limbs_degress), image.COLOR_GREEN)

                    center_point.update((left_lower_limbs_point.x + right_lower_limbs_point.x)//2, (left_lower_limbs_point.y + right_lower_limbs_point.y)//2)
                    if last_center_point.x == 0 or last_center_point.y == 0:
                        last_center_point.update(center_point.x, center_point.y)
                    img.draw_rect(center_point.x, center_point.y, 10, 10, image.COLOR_GREEN, -1)

                    jump = False
                    down = False
                    left = False
                    right = False
                    operation_count = 0

                    # jump
                    img.draw_line(0, up_max_y, img.width(), up_max_y, image.COLOR_RED, 2)
                    if center_point.y < up_max_y:
                        jump = True if upper_valid else False
                        upper_valid = False
                        operation_count = 1
                    else:
                        if not upper_valid:      # 从跳起刚落下, 重置中点
                            last_center_point.update(center_point.x, center_point.y)
                        upper_valid = True

                    # down
                    img.draw_line(0, down_min_y, img.width(), down_min_y, image.COLOR_RED, 2)
                    if center_point.y > down_min_y:
                        down = True if down_valid else False
                        down_valid = False
                        operation_count = 1
                    else:
                        if not down_valid:      # 从蹲下刚起身, 重置中点
                            last_center_point.update(center_point.x, center_point.y)
                        down_valid = True

                    # 左右肩膀偏移检测(不带检查)
                    if not jump and not down and left_or_right_valid:
                        # print("upper_limbs_degress", upper_limbs_degress)
                        if 0 < upper_limbs_degress < upper_limbs_base_degress - upper_limbs_offset_degress: # left
                            operation_count = 1
                            left = True
                            left_or_right_valid = False
                        elif 150 > upper_limbs_degress > upper_limbs_base_degress + upper_limbs_offset_degress: # right
                            operation_count = 1
                            right = True
                            left_or_right_valid = False
                        else: # center
                            pass

                    if not left_or_right_valid and abs(upper_limbs_base_degress - upper_limbs_degress) < upper_limbs_offset_degress:
                        left_or_right_valid = True

                    for _ in range(operation_count):
                        if jump:
                            self.press('up')
                        elif down:
                            self.press('down')
                        elif left:
                            self.press('left')
                        elif right:
                            self.press('right')
                        else:
                            pass

                    if jump or down or left or right:
                        print(f'time:{time.ticks_ms()} operation_count:{operation_count} jump:{jump} down:{down} left:{left} right:{right}')
                        last_not_action_ms = time.ticks_ms()
                    else:
                        if time.ticks_ms() - last_not_action_ms > 1000:
                            last_not_action_ms = time.ticks_ms()
                            if abs(center_point.y - abs(up_max_y + down_min_y)//2) > abs(up_max_y - down_min_y) * 0.4:
                                calibrate(final_obj, hmirror=self.play_game_need_mirror, without_limbs_degress=True)

                if time.ticks_ms() - last_disp_ms > 60:
                    # display.send_to_maixvision(img)       # 不在显示屏上显示, 更快
                    self.disp.show(img)
                    last_disp_ms = time.ticks_ms()

            print('loop cost', time.ticks_ms() - last_loop_ms)
            last_loop_ms = time.ticks_ms()
        del self.key_obj

if __name__ == '__main__':
    App().run()