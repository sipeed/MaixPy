import servos
from collections import deque
from maix import time, app, camera, image, display, touchscreen, nn, sys
import cv2
import numpy as np

# init uart register
SERVO_PORT_NAME =  '/dev/ttyS4' 	    # 舵机串口号
SERVO_BAUDRATE = 115200 	            # 舵机的波特率
SERVO_ID = [1, 2] 				        # 舵机ID,依次是pitch，roll，yaw
SERVO_MIN_POSITION = [1650, 0]          # 舵机位置最小值
SERVO_MAX_POSITION = [2446, 4096]       # 舵机位置最大值
value_per_angle = 4096 / 270
SERVO_ANGLE = [0, 0]                    # 舵机旋转的角度范围
for i, _ in enumerate(SERVO_ANGLE):
    SERVO_ANGLE[i] = (SERVO_MAX_POSITION[i] - SERVO_MIN_POSITION[i]) / value_per_angle
test_get_position_enable = False        # 测试读取舵机的位置， 时能后舵机关闭扭矩， 并且持续读出舵机的位置
test_set_pitch_position_enable = False  # 测试设置pitch方向的位置
test_set_roll_position_enable = False   # 测试设置roll方向的位置

# OS04D10 fov h=90, v=81
# SC850SL fov h=86.7, v=48.8
CAMERA_FOV_H = 86.7                       # 水平视场角， 查询镜头手册获取。
CAMERA_FOV_V = 48.8                       # 垂直视场角， 查询镜头手册获取。

# blobs_thresholds = [[0, 100, -31, -10, 83, 103]]
# blobs_thresholds = [[0, 100, -31, 12, 77, 103]]    # 小黄鸭 os04d10
blobs_thresholds = [[0, 100, -13, 12, 50, 75]]      # 小黄鸭 sc850sl
# blobs_thresholds = [[25, 80, -39, -19, 21, 41]]    # 绿色

blobs_area_threshold = 500              # blob最小面积
blobs_pixels_threshold = 500            # blob最小像素点

pitch_pid = [0.45, 0.00001, 0.000, 0]    # [P I D I_max]
roll_pid  = [0.6, 0.01, 0.000, 0]    # [P I D I_max]

manual_wb_enable = True                  # 使能手动白平衡，保证找色块时颜色不会随色温变化
wb_gain_list = [0.0682, 0, 0, 0.04897]   # 手动白平衡增益参数

pitch_reverse = True                   # reverse out value direction
roll_reverse = True                     # reverse out value direction

class RunningAverage:
    def __init__(self, n=5):
        self.n = n
        self.buf = deque(maxlen=n)
    def add(self, v):
        self.buf.append(v)
    def value(self):
        return sum(self.buf)/len(self.buf) if self.buf else 0.0

class Status:
    GET_RETANGLE = 0,
    DETECT = 1,

def rgb_list_to_lab_list(rgb_list):
    """
    将RGB列表转换为Lab列表
    rgb_list: [[r, g, b], [r, g, b], ...]，值范围0-255
    返回: [[L, a, b], [L, a, b], ...]
    """
    # 转换为numpy数组
    rgb_array = np.array(rgb_list, dtype=np.uint8).reshape(-1, 1, 3)
    
    # 转换为float并归一化
    rgb_float = rgb_array.astype(np.float32) / 255.0
    
    # 转换到Lab颜色空间
    lab_array = cv2.cvtColor(rgb_float, cv2.COLOR_RGB2LAB)
    
    # 转换回列表格式
    lab_list = lab_array.reshape(-1, 3).astype(int).tolist()
    
    return lab_list

class App:
    def __init__(self, gimbal: servos.Gimbal):
        self.cam = camera.Camera(640, 360)
        self.disp = display.Display()
        self.ts = touchscreen.TouchScreen()
        self.img_exit = image.load("./assets/exit.jpg").resize(40, 40)
        self.img_exit_touch = image.load("./assets/exit_touch.jpg").resize(40, 40)
        self.exit_box = [0, 0, self.img_exit.width(), self.img_exit.height()]
        self.need_exit = False

        if manual_wb_enable:
            self.cam.awb_mode(camera.AwbMode.Manual)
            self.cam.set_wb_gain(wb_gain_list)
        self.gimbal = gimbal
        self.smooth_pitch = RunningAverage()
        self.smooth_roll = RunningAverage()
        self.status = Status.GET_RETANGLE

    def check_touch_box(self, t, box, oft = 0):
        """This method is used for exiting and you normally do not need to modify or call it.
            You usually don't need to modify it.
        """
        if t[2] and t[0] + oft > box[0] and t[0] < box[0] + box[2] + oft and t[1] + oft > box[1] and t[1] < box[1] + box[3] + oft:
            return True
        else:
            return False

    def run(self):
        pressing = False
        target = nn.Object()
        btn_str = "Select"
        font_size = image.string_size(btn_str)

        while not app.need_exit():
            img = self.cam.read()
            touch_status = self.ts.read()
            if self.status == Status.GET_RETANGLE:
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
                        if target.w > 0 and target.h > 0:
                            print(f"Init with rectangle x: {target.x}, y: {target.y}, w: {target.w}, h: {target.h}")
                            rgb_list = img.get_pixel(target.x + target.w // 2, target.y + target.h // 2, True)
                            print('rgb list', rgb_list)
                            lab_list = rgb_list_to_lab_list(rgb_list)[0]
                            print('lab list', lab_list)
                            blobs_thresholds = [[lab_list[0] - 15, lab_list[0] + 15, lab_list[1] - 15, lab_list[1] + 15, lab_list[2] - 15, lab_list[2] + 15]]
                            print('blobs_thresholds', blobs_thresholds)
                            self.status = Status.DETECT
                        else:
                            print(f"Rectangle invalid, x: {target.x}, y: {target.y}, w: {target.w}, h: {target.h}")
                    pressing = False
                if pressing:
                    img.draw_string(2, img.height() - font_size[1] * 2, "Select and release to complete", image.Color.from_rgb(255, 0, 0), 1.5)
                    img.draw_rect(target.x, target.y, touch_status[0] - target.x, touch_status[1] - target.y, image.Color.from_rgb(255, 0, 0), 3)
                else:
                    img.draw_string(2, img.height() - font_size[1] * 2, "Select target on screen", image.Color.from_rgb(255, 0, 0), 1.5)
                self.disp.show(img)
            elif self.status == Status.DETECT:
                pitch_error = 0
                roll_error = 0
                if touch_status[2]:
                    self.status = Status.GET_RETANGLE
                img_w = img.width()
                img_h = img.height()
                obj_x = -1
                obj_y = -1
                blobs = img.find_blobs(blobs_thresholds, area_threshold = blobs_area_threshold, pixels_threshold = blobs_pixels_threshold)
                if len(blobs) > 0:
                    b = blobs[0]
                    corners = b.mini_corners()
                    obj_x = b.cx()
                    obj_y = b.cy()
                    
                    print(b.cx(), b.cy())
                    for i in range(4):
                        img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_RED, 4)

                if obj_x != -1 and obj_y != -1:
                    center_x = img_w / 2
                    center_y = img_h / 2
                    angle_x = (obj_x - center_x) / img_w * CAMERA_FOV_H
                    angle_y = (obj_y - center_y) / img_h * CAMERA_FOV_V
                    print(f'angle_x:{angle_x:.2f} fov_h:{CAMERA_FOV_H:.2f}', f'angle_y:{angle_y:.2f} fov_v:{CAMERA_FOV_V:.2f}')

                    # # 偏移的角度映射到舵机偏移的百分比
                    # pitch_error = (angle_y + SERVO_ANGLE[0] / 2) / SERVO_ANGLE[0] * 100
                    # roll_error = (angle_x + SERVO_ANGLE[1] / 2) / SERVO_ANGLE[1] * 100

                    # 偏移的角度转舵机旋转值
                    pitch_error = angle_y * value_per_angle
                    roll_error = angle_x * value_per_angle

                print(f'pitch_error:{pitch_error:.2f} pitch_angle_range:{SERVO_ANGLE[0]:.2f} roll_error:{roll_error:.2f} roll_angle_range:{SERVO_ANGLE[1]:.2f}')
                gimbal.run(pitch_error, roll_error, pitch_reverse = pitch_reverse, roll_reverse=roll_reverse)
            
                if self.need_exit:
                    app.set_exit_flag(True)
                    break

            img = img.resize(self.disp.width(), self.disp.height(), image.Fit.FIT_CONTAIN)
            if self.check_touch_box(touch_status, self.exit_box, 20):
                img.draw_image(self.exit_box[0], self.exit_box[1], self.img_exit_touch)
                self.need_exit = True
            else:
                img.draw_image(self.exit_box[0], self.exit_box[1], self.img_exit)

            self.disp.show(img)
if __name__ == '__main__':
    s = servos.Servos(SERVO_ID, SERVO_PORT_NAME, SERVO_BAUDRATE, SERVO_MIN_POSITION, SERVO_MAX_POSITION)
    pid_pitch = servos.PID(p=pitch_pid[0], i=pitch_pid[1], d=pitch_pid[2], imax=pitch_pid[3])
    pid_roll = servos.PID(p=roll_pid[0], i=roll_pid[1], d=roll_pid[2], imax=roll_pid[3])
    gimbal = servos.Gimbal(s, pid_pitch, pid_roll)

    if test_get_position_enable:
        s.test_position()
    elif test_set_pitch_position_enable:
        s.uservo.set_position(1, 2048)
        while True:
            pos = s.uservo.get_position(1)
            if pos:
                if pos > 2000 and pos < 3100:
                    break
            time.sleep_ms(1)

        t = time.ticks_us()
        s.uservo.set_position(1, 2548)
        while True:
            pos = s.uservo.get_position(1)
            if pos:
                if pos > 2548-50 and pos < 2548+50:
                    break
            time.sleep_ms(1)
        print('cost', time.ticks_us() - t)
    elif test_set_roll_position_enable:
        id = 2
        angle = 120
        start_position = 1024
        dst_position = start_position + angle / 270 * 4096
        s.uservo.set_position(id, start_position)
        
        while True:
            pos = s.uservo.get_position(id)
            if pos:
                if pos > start_position - 25 and pos < start_position + 25:
                    break
                print('wait start position, dst position', dst_position,'curr position', pos)
            time.sleep_ms(100)

        t = time.ticks_us()
        s.uservo.set_position(id, dst_position)
        print('run set_position cost', time.ticks_us() - t)

        t = time.ticks_us()
        while True:
            pos = s.uservo.get_position(id)
            if pos:
                if pos > dst_position-25 and pos < dst_position+100:
                    break
                print('wait dst position, dst position', dst_position,'curr position', pos)
            # time.sleep_ms(1)
        print('wait cost', time.ticks_us() - t)

        while not app.need_exit():
            pos = s.uservo.get_position(id)
            print(pos)
            time.sleep_ms(1000)
    else:
        a = App(gimbal)
        a.run()
