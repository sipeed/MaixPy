from maix import camera, display, image, app, time, touchscreen, key
from benchmarks.widgets import StrButton, ImgButton

def show_loading(disp):
    img = image.Image(disp.width(), disp.height(), bg=image.COLOR_BLACK)
    msg = "loading..."
    size = image.string_size(msg, scale=2, thickness=2)
    img.draw_string((img.width() - size.width()) // 2, (img.height() - size.height()) // 2, msg, image.COLOR_WHITE, scale=2, thickness=2)
    disp.show(img)
# no much module to import, so not show loading here
# disp = display.Display()
# show_loading(disp)

import math
import os
import importlib
import gc


def is_in_button(x, y, btn_pos):
    return x > btn_pos[0] and x < btn_pos[0] + btn_pos[2] and y > btn_pos[1] and y < btn_pos[1] + btn_pos[3]

class Program:
    def __init__(self):
        self.showing_result = False
        self.runing_case_obj = None
        self.key_obj = key.Key(self.on_key)
        self.disp = display.Display()
        show_loading(self.disp)

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
            img = image.Image(self.disp.width(), self.disp.height(), image.Format.FMT_RGBA8888, bg=image.Color.from_rgb(31, 31, 31))
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
                    print("del disp")
                    disp_w = self.disp.width()
                    disp_h = self.disp.height()
                    del self.disp
                    del ts
                    gc.collect()
                    print("construct item object")
                    self.runing_case_obj = items[curr_idx]()
                    case_name = self.runing_case_obj.name
                    print("run item", case_name)
                    try:
                        show, imgs = self.runing_case_obj.run()
                    except Exception:
                        import traceback
                        msg = traceback.format_exc()
                        print(msg)
                        img = image.Image(disp_w, disp_h, bg=image.COLOR_BLACK)
                        img.draw_string(0, 0, msg, image.COLOR_WHITE)
                        show = True
                        imgs = [img]
                    print(f"run item {case_name} end")
                    del self.runing_case_obj
                    self.runing_case_obj = None
                    gc.collect()
                    self.disp = display.Display()
                    ts = touchscreen.TouchScreen()
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
                            if type(img0) == str:
                                msg = img0
                                img0 = image.Image(self.disp.width(), self.disp.height(), bg=image.COLOR_BLACK)
                                size = image.string_size(msg, scale=2, thickness=2)
                                img0.draw_string((img0.width() - size.width()) // 2, (img0.height() - size.height()) // 2, msg, image.COLOR_WHITE, scale=2, thickness=2)
                            self.disp.show(img0)
                            if idx not in saved:
                                save_path = f"/root/benchmark/enchmark_result_{case_name}_{max(0, idx)}.png"
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
# del disp
program = Program()
try:
    while not app.need_exit():
        program.run()
except Exception:
    import traceback
    msg = traceback.format_exc()
    print(msg)
    disp = display.Display()
    img = image.Image(disp.width(), disp.height(), bg=image.COLOR_BLACK)
    img.draw_string(0, 0, msg, image.COLOR_WHITE)
    disp.show(img)
    program.showing_result = False
    program.runing_case_obj = None
    while not app.need_exit():
        time.sleep_ms(100)
