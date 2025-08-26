from maix import camera, display, image, app, time, touchscreen, key

disp = display.Display()
img = image.Image(disp.width(), disp.height(), bg=image.COLOR_BLACK)
msg = "loading..."
size = image.string_size(msg, scale=2, thickness=2)
img.draw_string((img.width() - size.width()) // 2, (img.height() - size.height()) // 2, msg, image.COLOR_WHITE, scale=2, thickness=2)
disp.show(img)
del img

import math
import os
import importlib
import gc

def is_in_button(x, y, btn_pos):
    return x > btn_pos[0] and x < btn_pos[0] + btn_pos[2] and y > btn_pos[1] and y < btn_pos[1] + btn_pos[3]

class StrButton:
    def __init__(self, label, img_w, img_h, disp_w, disp_h):
        self.pos = [0, 0]
        self.last_pushed_time = 0
        self.pushed = False
        self.update_vars(label, img_w, img_h, disp_w, disp_h)

    def update_vars(self, label, img_w, img_h, disp_w, disp_h):
        self.label = label
        self.img_w = img_w
        self.img_h = img_h
        self.disp_w = disp_w
        self.disp_h = disp_h
        self.scale = 2 if img_h >= 480 else 1.2
        self.thickness = 2
        self.string_size = image.string_size(self.label, scale=self.scale, thickness=self.thickness)
        self.padding = (self.string_size.height(), self.string_size.height() * 2 // 3)
        self.padding_2x = (int(self.padding[0] * 2), int(self.padding[1] * 2))
        self.btn_size = (self.string_size.width() + self.padding_2x[0], self.string_size.height() + self.padding_2x[1])
        self.set_pos(self.pos)

    def set_pos(self, pos):
        self.pos = pos
        self.rect = [self.pos[0], self.pos[1], self.btn_size[0], self.btn_size[1]]
        self.rect_disp = image.resize_map_pos(self.img_w, self.img_h, self.disp_w, self.disp_h, image.Fit.FIT_CONTAIN, self.rect[0], self.rect[1], self.rect[2], self.rect[3])

    def set_pos_lb(self, pos_lb):
        self.pos = (pos_lb[0], pos_lb[1] - self.btn_size[1])
        self.rect = [self.pos[0], self.pos[1], self.btn_size[0], self.btn_size[1]]
        self.rect_disp = image.resize_map_pos(self.img_w, self.img_h, self.disp_w, self.disp_h, image.Fit.FIT_CONTAIN, self.rect[0], self.rect[1], self.rect[2], self.rect[3])

    def set_pos_rt(self, pos_rt):
        self.pos = (pos_rt[0] - self.btn_size[0], pos_rt[1])
        self.rect = [self.pos[0], self.pos[1], self.btn_size[0], self.btn_size[1]]
        self.rect_disp = image.resize_map_pos(self.img_w, self.img_h, self.disp_w, self.disp_h, image.Fit.FIT_CONTAIN, self.rect[0], self.rect[1], self.rect[2], self.rect[3])

    def set_pos_rb(self, pos_rb):
        self.pos = (pos_rb[0] - self.btn_size[0], pos_rb[1] - self.btn_size[1])
        self.rect = [self.pos[0], self.pos[1], self.btn_size[0], self.btn_size[1]]
        self.rect_disp = image.resize_map_pos(self.img_w, self.img_h, self.disp_w, self.disp_h, image.Fit.FIT_CONTAIN, self.rect[0], self.rect[1], self.rect[2], self.rect[3])

    def set_pushed(self, pushed):
        self.pushed = pushed
        if self.pushed:
            self.last_pushed_time = time.ticks_ms()

    def draw(self, img):
        pushed = self.pushed
        if not pushed and time.ticks_ms() - self.last_pushed_time < 50:
            pushed = True
        if pushed:
            img.draw_rect(self.pos[0] + 1, self.pos[1] + 1, self.btn_size[0] - 1, self.btn_size[1] - 1, image.Color.from_rgb(0, 40, 138), thickness=-1)
            img.draw_rect(self.pos[0], self.pos[1], self.btn_size[0], self.btn_size[1], image.Color.from_rgb(0, 51, 182), thickness=1)
        else:
            img.draw_rect(self.pos[0] + 1, self.pos[1] + 1, self.btn_size[0] - 1, self.btn_size[1] - 1, image.Color.from_rgb(30, 83, 219), thickness=-1)
            img.draw_rect(self.pos[0], self.pos[1], self.btn_size[0], self.btn_size[1], image.Color.from_rgb(0, 51, 182), thickness=1)
        img.set_pixel(self.pos[0], self.pos[1], [31])
        img.set_pixel(self.pos[0] + self.btn_size[0] - 1, self.pos[1], [31])
        img.set_pixel(self.pos[0] + self.btn_size[0] - 1, self.pos[1] + self.btn_size[1] - 1, [31])
        img.set_pixel(self.pos[0], self.pos[1] + self.btn_size[1] - 1, [31])
        # img.draw_rect(self.pos[0] + self.padding[0], self.pos[1] + self.padding[1], self.string_size.width(), self.string_size.height(), image.COLOR_WHITE, thickness=1)
        img.draw_string(self.pos[0] + self.padding[0], self.pos[1] + self.padding[1] + 2, self.label, image.COLOR_WHITE, scale=self.scale, thickness=self.thickness)

class ImgButton:
    def __init__(self, img_path, img_pushed_path, img_w, img_h, disp_w, disp_h, padding = [0, 0]):
        self.btn_img = image.load(img_path, image.Format.FMT_RGBA8888)
        self.btn_img_pushed = image.load(img_pushed_path, image.Format.FMT_RGBA8888) if img_pushed_path else self.btn_img
        self.pos = [0, 0]
        self.padding = padding
        self.pushed = False
        self.last_pushed_time = 0
        self.update_vars(img_w, img_h, disp_w, disp_h)

    def update_vars(self, img_w, img_h, disp_w, disp_h):
        btn_img_h = int(img_h * 0.1)
        btn_img_w = int(btn_img_h * self.btn_img.width() / self.btn_img.height())
        if btn_img_h % 2 != 0:
            btn_img_h += 1
        if btn_img_w % 2 != 0:
            btn_img_w += 1
        if btn_img_h != self.btn_img.height() or btn_img_w != self.btn_img.width():
            self.btn_img = self.btn_img.resize(btn_img_w, btn_img_h, image.Fit.FIT_CONTAIN)
            self.btn_img_pushed = self.btn_img_pushed.resize(btn_img_w, btn_img_h, image.Fit.FIT_CONTAIN)
        self.img_w = img_w
        self.img_h = img_h
        self.disp_w = disp_w
        self.disp_h = disp_h
        self.padding_2x = (int(self.padding[0] * 2), int(self.padding[1] * 2))
        self.btn_size = (self.btn_img.width() + self.padding_2x[0], self.btn_img.height() + self.padding_2x[1])
        self.rect = [self.pos[0], self.pos[1], self.btn_size[0], self.btn_size[1]]
        self.rect_disp = image.resize_map_pos(self.img_w, self.img_h, self.disp_w, self.disp_h, image.Fit.FIT_CONTAIN, self.rect[0], self.rect[1], self.rect[2], self.rect[3])

    def set_pos(self, pos):
        self.pos = pos
        self.rect = [self.pos[0], self.pos[1], self.btn_size[0], self.btn_size[1]]
        self.rect_disp = image.resize_map_pos(self.img_w, self.img_h, self.disp_w, self.disp_h, image.Fit.FIT_CONTAIN, self.rect[0], self.rect[1], self.rect[2], self.rect[3])

    def set_pos_lb(self, pos_lb):
        self.pos = (pos_lb[0], pos_lb[1] - self.btn_size[1])
        self.rect = [self.pos[0], self.pos[1], self.btn_size[0], self.btn_size[1]]
        self.rect_disp = image.resize_map_pos(self.img_w, self.img_h, self.disp_w, self.disp_h, image.Fit.FIT_CONTAIN, self.rect[0], self.rect[1], self.rect[2], self.rect[3])

    def set_pos_rt(self, pos_rt):
        self.pos = (pos_rt[0] - self.btn_size[0], pos_rt[1])
        self.rect = [self.pos[0], self.pos[1], self.btn_size[0], self.btn_size[1]]
        self.rect_disp = image.resize_map_pos(self.img_w, self.img_h, self.disp_w, self.disp_h, image.Fit.FIT_CONTAIN, self.rect[0], self.rect[1], self.rect[2], self.rect[3])

    def set_pos_rb(self, pos_rb):
        self.pos = (pos_rb[0] - self.btn_size[0], pos_rb[1] - self.btn_size[1])
        self.rect = [self.pos[0], self.pos[1], self.btn_size[0], self.btn_size[1]]
        self.rect_disp = image.resize_map_pos(self.img_w, self.img_h, self.disp_w, self.disp_h, image.Fit.FIT_CONTAIN, self.rect[0], self.rect[1], self.rect[2], self.rect[3])

    def set_pushed(self, pushed):
        self.pushed = pushed
        if self.pushed:
            self.last_pushed_time = time.ticks_ms()

    def draw(self, img):
        pushed = self.pushed
        if not pushed and time.ticks_ms() - self.last_pushed_time < 50:
            pushed = True
        if pushed:
            if img.format() != self.btn_img_pushed.format():
                self.btn_img_pushed = self.btn_img_pushed.to_format(img.format())
            img.draw_image(self.pos[0] + self.padding[0], self.pos[1] + self.padding[1], self.btn_img_pushed)
        else:
            if img.format() != self.btn_img.format():
                self.btn_img = self.btn_img.to_format(img.format())
            img.draw_image(self.pos[0] + self.padding[0], self.pos[1] + self.padding[1], self.btn_img)


class Program:
    def __init__(self, disp):
        self.showing_result = False
        self.runing_case_obj = None
        self.key_obj = key.Key(self.on_key)
        self.disp = disp

    def on_key(self, key_id, state):
        '''
            this func called in a single thread
        '''
        print(f"main on_key key: {key_id}, state: {state}") # key.c or key.State.KEY_RELEASED
        if self.runing_case_obj is not None and hasattr(self.runing_case_obj, "on_key"):
            self.runing_case_obj.on_key(key_id, state)
        elif state == key.State.KEY_PRESSED:
                if self.showing_result:
                    self.showing_result = False
                else:
                    app.set_exit_flag(True)

    def get_benchmark_items(self):
        files = os.listdir("benchmarks")
        files.sort()
        classes = []
        for name in files:
            name, ext = os.path.splitext(name)
            if name.startswith("benchmark_") and name != "benchmark_base":
                module_name = "benchmarks." + name
                module = importlib.import_module(module_name)
                classes.append(getattr(module, "Bechmark"))
        return classes

    def draw_hint_rects(self, img, curr_idx, items_len, y, str_size):
        max_w = str_size.height() // 3
        rect_size = min(max_w, img.width() / items_len // 2)
        padding = int(rect_size * 0.5)
        y = y + rect_size
        total_w = items_len * rect_size + (items_len - 1) * padding
        x = (img.width() - total_w) // 2
        for i in range(items_len):
            if i == curr_idx:
                img.draw_rect(x, y, rect_size, rect_size, image.Color.from_rgb(30, 136, 229), thickness=-1)
            else:
                smal_size = rect_size // 2
                img.draw_rect(x + smal_size // 2, y + smal_size // 2, smal_size, smal_size, image.Color.from_rgb(30, 136, 229), thickness=-1)
            x += rect_size + padding

    def run(self):
        touch_pressed = False
        ts = touchscreen.TouchScreen()
        if self.disp.height() >= 480:
            font_scale = 2.3
            title_font_scale = 3
        elif self.disp.height() >= 240:
            font_scale = 1.4
            title_font_scale = 2.1
        btn_mode = StrButton("Mode", self.disp.width(), self.disp.height(), self.disp.width(), self.disp.height())
        btn_mode.set_pos_lb((0, self.disp.height()))
        btn_start = StrButton("Start", self.disp.width(), self.disp.height(), self.disp.width(), self.disp.height())
        btn_start.set_pos_rb((self.disp.width(), self.disp.height()))
        btn_back = ImgButton("/maixapp/share/icon/ret.png", "/maixapp/share/icon/ret2.png", self.disp.width(), self.disp.height(), self.disp.width(), self.disp.height(), padding=(4, 4))
        btn_back.set_pos((0, 0))

        items = self.get_benchmark_items()
        curr_idx = 0
        press_start_pos = [-1, -1]

        while not app.need_exit():
            img = image.Image(disp.width(), disp.height(), image.Format.FMT_RGBA8888, bg=image.Color.from_rgb(31, 31, 31))
            # draw buttons
            btn_back.draw(img)
            btn_mode.draw(img)
            btn_start.draw(img)
            # draw item name
            label = items[curr_idx].name
            label_size = image.string_size(label, scale=title_font_scale, thickness=title_font_scale)
            y = (img.height() - label_size.height()) // 2
            img.draw_string((img.width() - label_size.width()) // 2, y, label, scale=title_font_scale, thickness=title_font_scale)
            # draw hint rects
            self.draw_hint_rects(img, curr_idx, len(items), y + label_size.height(), label_size)
            x, y, preesed = ts.read()
            if preesed:
                touch_pressed = True
                if is_in_button(x, y, btn_mode.rect_disp):
                    btn_mode.set_pushed(True)
                elif is_in_button(x, y, btn_start.rect_disp):
                    btn_start.set_pushed(True)
                elif is_in_button(x, y, btn_back.rect_disp):
                    btn_back.set_pushed(True)
                if press_start_pos[0] < 0 or press_start_pos[1] < 0:
                    press_start_pos = [x, y]
            elif touch_pressed:
                touch_pressed = False
                btn_mode.set_pushed(False)
                btn_start.set_pushed(False)
                btn_back.set_pushed(False)
                if is_in_button(x, y, btn_back.rect_disp):
                    app.set_exit_flag(True)
                elif is_in_button(x, y, btn_mode.rect_disp):
                    curr_idx = (curr_idx + 1) % len(items)
                    print("switch mode")
                elif is_in_button(x, y, btn_start.rect_disp):
                    self.runing_case_obj = items[curr_idx](self.disp, ts)
                    print("run item", self.runing_case_obj.name)
                    show, imgs = self.runing_case_obj.run()
                    print(f"run item {self.runing_case_obj.name} end")
                    # show result
                    if show:
                        print("show result, press any key to exit")
                        idx = 0
                        if not isinstance(imgs, (list, tuple)):
                            imgs = [imgs]
                        img_len = len(imgs)
                        self.showing_result = img_len > 0
                        saved = []
                        btn_back2 = ImgButton("/maixapp/share/icon/ret.png", "/maixapp/share/icon/ret2.png", self.disp.width(), self.disp.height(), self.disp.width(), self.disp.height(), padding=(4, 4))
                        while self.showing_result and not app.need_exit():
                            img0 = imgs[idx]
                            self.disp.show(img0)
                            if idx not in saved:
                                save_path = f"/root/benchmark/enchmark_result_{self.runing_case_obj.name}_{max(0, idx)}.png"
                                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                                print(f"save to {save_path}")
                                img0.save(save_path)
                                saved.append(idx)
                                curr_res_idx = max(idx, 0) + 1
                                msg =f"{curr_res_idx} / {img_len}, touch to next"
                                size = image.string_size(msg, scale=font_scale)
                                img0.draw_string(img0.width() - size.width() - size.height(), img0.height() - size.height(), msg, image.COLOR_WHITE, scale=font_scale)
                            btn_back2.update_vars(img0.width(), img0.height(), self.disp.width(), self.disp.height())
                            btn_back2.set_pos_lb((0, img0.height()))
                            btn_back2.draw(img0)
                            self.disp.show(img0)
                            while ts.available():
                                x, y, touch_pressed = ts.read()
                            while self.showing_result:
                                x, y, preesed = ts.read()
                                if preesed:
                                    touch_pressed = True
                                elif touch_pressed:
                                    touch_pressed = False
                                    idx = (idx + 1) % img_len
                                    if is_in_button(x, y, btn_back2.rect_disp):
                                        self.showing_result = False
                                    break
                                time.sleep_ms(50)
                    del self.runing_case_obj
                    self.runing_case_obj = None
                    gc.collect()
                else:
                    # move left right
                    dx = x - press_start_pos[0]
                    if abs(dx) > self.disp.width() / 5:
                        if dx > 0:
                            curr_idx = (curr_idx - 1) % len(items)
                        else:
                            curr_idx = (curr_idx + 1) % len(items)
                        print("switch mode by swipe")
                    press_start_pos = [-1, -1]
            # if press_start_pos[0] >= 0 and press_start_pos[1] >= 0:
            #     img.draw_line(press_start_pos[0], press_start_pos[1], x, y, image.COLOR_GRAY, thickness=2)
            try:
                self.disp.show(img)
            except Exception:
                print("show img failed")

program = Program(disp)
try:
    while not app.need_exit():
        program.run()
except Exception:
    import traceback
    msg = traceback.format_exc()
    print(msg)
    img = image.Image(disp.width(), disp.height(), bg=image.COLOR_BLACK)
    img.draw_string(0, 0, msg, image.COLOR_WHITE)
    disp.show(img)
    program.showing_result = False
    program.runing_case_obj = None
    while not app.need_exit():
        time.sleep_ms(100)
