

from maix import image, time, display, camera, nn, app, sys, touchscreen, key, err
import gc
import threading
import os
import re
import subprocess
import signal
import numpy as np
from collections import deque
from datetime import datetime
from .widgets import StrButton

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

class Bechmark:
    name = "Stress"

    def __init__(self):
        self.repeat_time = 50
        self.disp = display.Display()
        self.disp_ui = self.disp.add_channel()
        self.ts = touchscreen.TouchScreen()
        self.read_interval = 2 # s
        self.cpu_temp_record_time = 180 # s
        self.cpu_temp_record_len = self.cpu_temp_record_time // self.read_interval
        self.cpu_temp_values = deque(maxlen=self.cpu_temp_record_len)
        self.cpu_temp_max = 100
        self.cpu_temp_min = 30
        self.last_read_cpu_temp = 0
        self.fps_values = deque(maxlen=self.cpu_temp_record_len)
        self.need_exit = False
        self.restarting = True
        self.cam = None
        self.cam_res_list = [(self.disp.width(), self.disp.height()), (1280, 720), (1920, 1080), (2560, 1440)]
        self.support_ai_isp = sys.device_id() in ["maixcam2"]

    def __del__(self):
        self.destroy_cam()

    def on_key(self, key_id, state):
        print("stress on_key", key_id, state)
        if state == key.State.KEY_PRESSED:
            self.need_exit = True

    def init_cam(self, res):
        self.destroy_cam()
        self.cam = camera.Camera(res[0], res[1])
        self.line_thickness = (8 if self.cam.height() >= 1080 else 4) if self.cam.height() >= 480 else 2

    def destroy_cam(self):
        if self.cam is not None:
            del self.cam
            del self.disp_ui
            del self.disp
            gc.collect()
            self.cam = None
            self.disp = display.Display()
            self.disp_ui = self.disp.add_channel()

    def npu_out_reader(self, pipe, model_fps):
        try:
            for line in iter(pipe.readline, ''):
                if line:
                    # [running result] fps: 12.34
                    match = re.search(r"\[running result\].*fps:\s*([0-9.]+)", line)
                    if match:
                        fps = float(match.group(1))
                        model_fps[0] = fps
        finally:
            pipe.close()

    def stress_thread(self, model_name):
        '''
            make sure CPU full load
        '''
        print("stress_thread start")
        cam_res_curr_idx = 0
        record_path = f"/root/benchmark/benchmark_stress_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
        os.makedirs(os.path.dirname(record_path), exist_ok=True)
        f = open(record_path, "w")
        while self.restarting:
            disp_err_times = 0

            err_count = 0
            while 1:
                try:
                    self.init_cam(self.cam_res_list[cam_res_curr_idx])
                    break
                except Exception as e:
                    print(f"Init cam with {self.cam_res_list[cam_res_curr_idx]} failed,", e)
                    err_count += 1
                    cam_res_curr_idx = (cam_res_curr_idx + 1) % len(self.cam_res_list)
                    if err_count >= len(self.cam_res_list):
                        print(f"error {err_count} times, now exit !!")
                        self.need_exit = True
                        break
                    continue

            cpu_temp = 0
            self.cpu_usage = 0
            npu_usage = 0
            cpu_freq = 0
            npu_freq = 0
            def update_res_vars():
                if self.disp_ui.height() >= 1440:
                    self.font_scale = 5
                    self.font_thickness = 5
                elif self.disp_ui.height() >= 1080:
                    self.font_scale = 4
                    self.font_thickness = 4
                elif self.disp_ui.height() >= 720:
                    self.font_scale = 2.5
                    self.font_thickness = 3
                elif self.disp_ui.height() >= 480:
                    self.font_scale = 1.4
                    self.font_thickness = 2
                else:
                    self.font_scale = 1
                    self.font_thickness = 1
                self.font_size = image.string_size("aA!~?/", scale = self.font_scale)
                self.ai_isp_on = True if app.get_sys_config_kv("npu", "ai_isp", "0") == "1" else False
                self.font_margin = self.font_size.height() // 2
                self.button_padding = 15 if self.disp.height() >= 480 else 8
                self.button_padding_2x = self.button_padding * 2
                self.btn_cam_res = StrButton("Cam res", self.disp_ui.width(), self.disp_ui.height(), self.disp.width(), self.disp.height())
                self.btn_cam_res.set_pos_lb((0, self.disp_ui.height()))
                if self.support_ai_isp:
                    self.btn_ai_isp = StrButton(f"AI ISP: {'ON' if self.ai_isp_on else 'OFF'}", self.disp_ui.width(), self.disp_ui.height(), self.disp.width(), self.disp.height(), True, self.ai_isp_on)
                    self.btn_ai_isp.set_pos_lb((self.btn_cam_res.rect[2] + self.button_padding, self.disp_ui.height()))
                self.img_back = image.load("/maixapp/share/icon/ret.png")
                self.img_back = get_back_btn_img(self.disp_ui.width())
                back_rect = [0, 0, self.img_back.width() + self.button_padding_2x, self.img_back.height() + self.button_padding_2x]
                self.back_rect_disp = image.resize_map_pos(self.disp_ui.width(), self.disp_ui.height(), self.disp.width(), self.disp.height(), image.Fit.FIT_CONTAIN, back_rect[0], back_rect[1], back_rect[2], back_rect[3])

            update_res_vars()

            self.restarting = False
            touch_pressed = False
            last_fps_y = 0
            last_temp_y = 0
            while (not self.need_exit) and (not app.need_exit()):
                if time.ticks_s() - self.last_read_cpu_temp > self.read_interval:
                    self.last_read_cpu_temp = time.ticks_s()
                    cpu_temp = sys.cpu_temp()["cpu"]
                    self.cpu_temp_values.append(cpu_temp)
                    self.fps_values.append(self.model_fps[0])
                    self.cpu_usage = sys.cpu_usage()["cpu"]
                    npu_usage = sys.npu_usage()["npu"]
                    cpu_freq = sys.cpu_freq()["cpu0"]
                    npu_freq = sys.npu_freq()["npu0"]
                    f.write(f"{time.time()}, {cpu_temp}, {self.cpu_usage}, {npu_usage}\n")
                    f.flush()
                img = image.Image(self.disp_ui.width(), self.disp_ui.height(), image.Format.FMT_BGRA8888, bg = image.Color.from_bgra(0, 0, 0, 0))

                # draw lines
                y = int((80 - self.cpu_temp_min) / (self.cpu_temp_max - self.cpu_temp_min) * img.height())
                img.draw_line(0, img.height() - y, img.width(), img.height() - y, image.COLOR_WHITE, thickness=1)
                y = int((70 - self.cpu_temp_min) / (self.cpu_temp_max - self.cpu_temp_min) * img.height())
                img.draw_line(0, img.height() - y, img.width(), img.height() - y, image.COLOR_WHITE, thickness=1)
                y = int((60 - self.cpu_temp_min) / (self.cpu_temp_max - self.cpu_temp_min) * img.height())
                img.draw_line(0, img.height() - y, img.width(), img.height() - y, image.COLOR_WHITE, thickness=1)
                img.draw_string(0, img.height() - y + 2, "60", image.COLOR_YELLOW, scale=self.font_scale, thickness=self.font_thickness)
                y = int((50 - self.cpu_temp_min) / (self.cpu_temp_max - self.cpu_temp_min) * img.height())
                img.draw_line(0, img.height() - y, img.width(), img.height() - y, image.COLOR_WHITE, thickness=1)
                img.draw_string(0, img.height() - y + 2, "50", image.COLOR_YELLOW, scale=self.font_scale, thickness=self.font_thickness)

                # draw graph
                # draw cpu temp
                padding = img.width() // self.cpu_temp_record_len
                x = img.width() - len(self.cpu_temp_values) * padding + padding // 2
                last = None
                last_fps = None
                for i, temp in enumerate(self.cpu_temp_values):
                    y = img.height() - int((temp - self.cpu_temp_min) / (self.cpu_temp_max - self.cpu_temp_min) * img.height())
                    fps_value = self.model_fps[0] if i == len(self.cpu_temp_values) - 1 else self.fps_values[i]
                    y2 = (fps_value - self.cpu_temp_min) / (self.cpu_temp_max - self.cpu_temp_min) 
                    y2 = 100 if y2 > 100 else y2
                    y2 = img.height() - int(y2 * img.height())
                    if last is None:
                        first_record_time = (len(self.cpu_temp_values) - 1) * self.read_interval
                        if first_record_time > 10:
                            img.draw_string(x, y, f"{-first_record_time}s", image.COLOR_RED, scale=self.font_scale, thickness=2)
                    else:
                        img.draw_line(last_fps[0], last_fps[1], x, y2, image.COLOR_PURPLE, self.line_thickness)
                        img.draw_line(last[0], last[1], x, y, image.COLOR_RED, self.line_thickness)
                    last = [x, y]
                    last_fps = [x, y2]
                    x += padding

                # draw info
                y = self.img_back.height() + self.button_padding_2x
                img.draw_string(2, y, f"[CPU] usage: {self.cpu_usage:3.1f}%, temp: {cpu_temp:3.1f} C, freq: {cpu_freq // 1000000}MHz", image.COLOR_WHITE, scale=self.font_scale, thickness=self.font_thickness * 2)
                img.draw_string(2, y, f"[CPU] usage: {self.cpu_usage:3.1f}%, temp: {cpu_temp:3.1f} C, freq: {cpu_freq // 1000000}MHz", image.COLOR_RED, scale=self.font_scale, thickness=self.font_thickness)
                y += self.font_size.height() + self.font_margin
                img.draw_string(2, y, f"[NPU] usage: {npu_usage:3.1f}%{(', AI ISP: ON' if self.ai_isp_on else ', AI ISP: OFF') if self.support_ai_isp else ''}, freq: {npu_freq // 1000000}MHz", image.COLOR_WHITE, scale=self.font_scale, thickness=self.font_thickness * 2)
                img.draw_string(2, y, f"[NPU] usage: {npu_usage:3.1f}%{(', AI ISP: ON' if self.ai_isp_on else ', AI ISP: OFF') if self.support_ai_isp else ''}, freq: {npu_freq // 1000000}MHz", image.COLOR_RED, scale=self.font_scale, thickness=self.font_thickness)
                y += self.font_size.height() + self.font_margin
                img.draw_string(2, y, f"model FPS: {self.model_fps[0]:3.1f}, model: {model_name}", image.COLOR_WHITE, scale=self.font_scale, thickness=self.font_thickness * 2)
                img.draw_string(2, y, f"model FPS: {self.model_fps[0]:3.1f}, model: {model_name}", image.COLOR_PURPLE, scale=self.font_scale, thickness=self.font_thickness)
                y += self.font_size.height() + self.font_margin
                fps = time.fps()
                img.draw_string(2, y, f"[CAM] {self.cam.width()}x{self.cam.height()}, fps: {self.cam.fps()}, {fps:.0f}", image.COLOR_WHITE, scale=self.font_scale, thickness=self.font_thickness * 2)
                img.draw_string(2, y, f"[CAM] {self.cam.width()}x{self.cam.height()}, fps: {self.cam.fps()}, {fps:.0f}", image.COLOR_RED, scale=self.font_scale, thickness=self.font_thickness)

                # draw npu fps number
                msg = f"{self.model_fps[0]:3.1f}fps"
                msg_size = image.string_size(msg, scale=self.font_scale)
                last_fps[1] = max(min(last_fps[1], img.height() - msg_size.height() - 2), 0)
                last_fps_y = last_fps_y * 0.7 + last_fps[1] * 0.3
                img.draw_string(last_fps[0] - msg_size.width() - 2, int(last_fps_y), msg, image.COLOR_PURPLE, scale=self.font_scale, thickness=self.font_thickness * 2)
                img.draw_string(last_fps[0] - msg_size.width() - 2, int(last_fps_y), msg, image.COLOR_WHITE, scale=self.font_scale, thickness=self.font_thickness)
                #draw temp number
                msg = f"{cpu_temp:3.1f} C"
                msg_size = image.string_size(msg, scale=self.font_scale)
                if last[1] >= last_fps[1] - msg_size.height() and last[1] <= last_fps[1] + msg_size.height():
                    last[1] = last_fps[1] + msg_size.height() + 2 if last[1] >= last_fps[1] else last_fps[1] - msg_size.height() - 2
                last[1] = max(min(last[1], img.height() - msg_size.height() - 2), 0)
                last_temp_y = last_temp_y * 0.7 + last[1] * 0.3
                img.draw_string(last[0] - msg_size.width() - 2, int(last_temp_y), msg, image.COLOR_RED, scale=self.font_scale, thickness=self.font_thickness * 2)
                img.draw_string(last[0] - msg_size.width() - 2, int(last_temp_y), msg, image.COLOR_WHITE, scale=self.font_scale, thickness=self.font_thickness)

                # draw buttons
                img.draw_image(0, 0, self.img_back)
                self.btn_cam_res.draw(img)
                if self.support_ai_isp:
                    self.btn_ai_isp.draw(img)

                try:
                    ret = self.disp_ui.show(img)
                    if ret != err.Err.ERR_NONE:
                        disp_err_times += 1
                        print("disp.show err:", ret)
                    else:
                        disp_err_times = 0
                except Exception:
                    print("show failed")
                    disp_err_times += 1
                if disp_err_times > 5:
                    self.err_msg = "Display show failed"
                    self.need_exit = True
                    break
                x, y, preesed = self.ts.read()
                if preesed:
                    touch_pressed = True
                    if is_in_button(x, y, self.back_rect_disp):
                        break
                    elif is_in_button(x, y, self.btn_cam_res.rect_disp):
                        self.btn_cam_res.set_pushed(True)
                    elif self.support_ai_isp and is_in_button(x, y, self.btn_ai_isp.rect_disp):
                        self.btn_ai_isp.set_pushed(True)
                elif touch_pressed:
                    touch_pressed = False
                    self.btn_cam_res.set_pushed(False)
                    if self.support_ai_isp:
                        self.btn_ai_isp.set_pushed(False)
                    if is_in_button(x, y, self.back_rect_disp):
                        self.need_exit = True
                        break
                    elif is_in_button(x, y, self.btn_cam_res.rect_disp):
                        cam_res_curr_idx = (cam_res_curr_idx + 1) % len(self.cam_res_list)
                        print("switch cam res to", self.cam_res_list[cam_res_curr_idx])
                        self.restarting = True
                        break
                    elif self.support_ai_isp and is_in_button(x, y, self.btn_ai_isp.rect_disp):
                        app.set_sys_config_kv("npu", "ai_isp", "0" if self.ai_isp_on else "1")
                        self.restarting = True
                        break
                time.sleep_us(100) # release CPU to ensure stress_thread running
            msg = ("Restarting" if self.restarting else "Exiting") + ", please wait..."
            print("ui thread exit", self.need_exit, app.need_exit(), msg)
            # draw message center
            img = image.Image(self.disp_ui.width(), self.disp_ui.height(), bg=image.Color.from_rgb(31, 31, 31))
            size = image.string_size(msg, scale=self.font_scale)
            img.draw_string((self.disp_ui.width() - size.width()) // 2, (self.disp_ui.height() - size.height()) // 2, msg, image.COLOR_WHITE, scale=self.font_scale, thickness=2)
            self.disp_ui.show(img)
        print("stress_thread exit")
        self.need_exit = True

    def run(self):
        last_ai_isp_config = app.get_sys_config_kv("npu", "ai_isp", "0")
        self.need_exit = False
        self.err_msg = None
        self.restarting = True
        disp_err_times = 0
        model_path = "/root/models/yolo11s.mud"
        if not os.path.exists(model_path):
            model_path = "/root/models/yolo11n.mud"
        model_name = os.path.basename(model_path)
        self.model_fps = [0]
        run_npu_py = os.path.abspath(os.path.join(os.path.dirname(__file__), "stress_run_npu.py"))
        command = ["/usr/bin/python", "-u", run_npu_py ]
        npu_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        t_out = threading.Thread(target=self.npu_out_reader, args=(npu_process.stdout, self.model_fps))
        t_out.daemon = True
        t_out.start()

        th = threading.Thread(target=self.stress_thread, args=(model_name,))
        th.daemon = True
        th.start()

        cam_res_curr_idx = 0

        while (not self.need_exit) and (not app.need_exit()):
            try:
                if self.restarting:
                    time.sleep_ms(10)
                    continue
                img = self.cam.read()
                ret = self.disp.show(img)
                if ret != err.Err.ERR_NONE:
                    disp_err_times += 1
                    print("disp.show err:", ret)
                else:
                    disp_err_times = 0
            except Exception:
                print("show failed")
                disp_err_times += 1
            time.sleep_ms(10) # release CPU to ensure stress_thread running
        print("main thread exit", self.need_exit, app.need_exit())
        self.need_exit = True
        # nee_exit.value = 1
        # draw message center
        img = image.Image(self.disp.width(), self.disp.height(), bg=image.Color.from_rgb(31, 31, 31))
        msg = ("Restarting" if self.restarting else "Exiting") + ", please wait..."
        size = image.string_size(msg, scale=self.font_scale)
        img.draw_string((self.disp.width() - size.width()) // 2, (self.disp.height() - size.height()) // 2, msg, image.COLOR_WHITE, scale=self.font_scale, thickness=2)
        self.disp.show(img)
        # kill p
        if npu_process.poll() is None:
            npu_process.send_signal(signal.SIGINT)
            t = time.ticks_ms()
            while npu_process.poll() is None and time.ticks_ms() - t < 5000:
                time.sleep_ms(100)
            if npu_process.poll() is None:
                print("stress_process is still alive, kill it")
                npu_process.kill()
        else:
            print("stress_process exit ok")
        self.destroy_cam()

        app.set_sys_config_kv("npu", "ai_isp", last_ai_isp_config)
        if self.err_msg:
            return True, self.err_msg
        return False, None

if __name__ == "__main__":

    disp = display.Display()
    ts = touchscreen.TouchScreen()
    obj = Bechmark(disp, ts)
    img = obj.run()
    disp.show(img)
    while not app.need_exit():
        time.sleep_ms(10)
