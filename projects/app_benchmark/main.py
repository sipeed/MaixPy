from maix import camera, display, image, app, time, touchscreen, key

disp = display.Display()
img = image.Image(disp.width(), disp.height())
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
        classes = []
        for name in files:
            name, ext = os.path.splitext(name)
            if name.startswith("benchmark_") and name != "benchmark_base":
                module_name = "benchmarks." + name
                module = importlib.import_module(module_name)
                classes.append(getattr(module, "Bechmark"))
        return classes

    def run(self):
        touch_pressed = False
        ts = touchscreen.TouchScreen()
        img_back = image.load("/maixapp/share/icon/ret.png")
        if self.disp.height() > 480:
            img_back = img_back.resize(96, int(96 / img_back.width() * img_back.height()))
            font_scale = 2.3
            title_font_scale = 3
        elif self.disp.height() > 240:
            img_back = img_back.resize(48, int(48 / img_back.width() * img_back.height()))
            font_scale = 1.4
            title_font_scale = 2.1
        string_mode = "Switch Item"
        string_start = "Start"
        button_padding = 10
        button_padding_2x = button_padding * 2
        string_mode_size = image.string_size(string_mode, scale=font_scale)
        string_start_size = image.string_size(string_start, scale=font_scale)
        back_rect = [0, 0, img_back.width() + button_padding_2x, img_back.height() + button_padding_2x]
        mode_rect = [0, self.disp.height() - string_mode_size.height() - button_padding_2x, string_mode_size.width() + button_padding_2x, string_mode_size.height() + button_padding_2x]
        start_rect = [self.disp.width() - string_start_size.width() - button_padding_2x, disp.height() - string_start_size.height() - button_padding_2x, string_start_size.width() + button_padding_2x, string_start_size.height() + button_padding_2x]
        back_rect_disp = image.resize_map_pos(self.disp.width(), self.disp.height(), self.disp.width(), self.disp.height(), image.Fit.FIT_CONTAIN, back_rect[0], back_rect[1], back_rect[2], back_rect[3])
        mode_rect_disp = image.resize_map_pos(self.disp.width(), self.disp.height(), self.disp.width(), self.disp.height(), image.Fit.FIT_CONTAIN, mode_rect[0], mode_rect[1], mode_rect[2], mode_rect[3])
        start_rect_disp = image.resize_map_pos(self.disp.width(), self.disp.height(), self.disp.width(), self.disp.height(), image.Fit.FIT_CONTAIN, start_rect[0], start_rect[1], start_rect[2], start_rect[3])

        items = self.get_benchmark_items()
        curr_idx = 0

        while not app.need_exit():
            img = image.Image(disp.width(), disp.height(), bg=image.COLOR_BLACK)
            img.draw_image(0, 0, img_back)
            img.draw_rect(mode_rect[0], mode_rect[1], mode_rect[2], mode_rect[3], image.COLOR_WHITE, thickness = 2)
            img.draw_rect(start_rect[0], start_rect[1], start_rect[2], start_rect[3], image.COLOR_WHITE, thickness = 2)
            img.draw_string(mode_rect[0] + button_padding, mode_rect[1] + button_padding, string_mode, scale=font_scale)
            img.draw_string(start_rect[0] + button_padding, start_rect[1] + button_padding, string_start, scale=font_scale)
            label = items[curr_idx].name
            label_size = image.string_size(label, scale=2, thickness=3)
            img.draw_string((img.width() - label_size.width()) // 2, (img.height() - label_size.height()) // 2, label, scale=title_font_scale, thickness=3)
            try:
                self.disp.show(img)
            except Exception:
                print("show img failed")
            x, y, preesed = ts.read()
            if preesed:
                touch_pressed = True
            elif touch_pressed:
                touch_pressed = False
                if is_in_button(x, y, back_rect_disp):
                    app.set_exit_flag(True)
                elif is_in_button(x, y, mode_rect_disp):
                    curr_idx = (curr_idx + 1) % len(items)
                    print("switch mode")
                elif is_in_button(x, y, start_rect_disp):
                    self.runing_case_obj = items[curr_idx](self.disp, ts)
                    print("run item", self.runing_case_obj.name)
                    show, img = self.runing_case_obj.run()
                    print(f"run item {self.runing_case_obj.name} end")
                    del self.runing_case_obj
                    self.runing_case_obj = None
                    gc.collect()
                    # show result
                    if show:
                        print("show result, press any key to exit")
                        self.showing_result = True
                        self.disp.show(img)
                        while self.showing_result:
                            x, y, preesed = ts.read()
                            if preesed:
                                touch_pressed = True
                            elif touch_pressed:
                                touch_pressed = False
                                self.showing_result = False
                                break
                            time.sleep_ms(50)

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
