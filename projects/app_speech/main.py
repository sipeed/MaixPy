from maix import display, touchscreen, app, image, time, audio
import importlib, threading

class ModuleLoader():
    def __load_module(self):
        self.module = importlib.import_module(self.module_name)
        self.load_ok = True
        pass
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.module = None
        self.load_ok = False
        self.t = threading.Thread(target=self.__load_module)
        self.t.start()
    def try_get_module(self, block = True):
        if self.load_ok:
            return self.module
        if block:
            while not self.load_ok:
                time.sleep_ms(100)
            return self.module
        else:
            return None

class AppStatus:
    IDLE = 1,
    RECORDING = 2,
    TRANSCRIBE = 3,

class App:
    def __init__(self):
        self.language = 'en'
        image.load_font("sourcehansans", "/maixapp/share/font/SourceHanSansCN-Regular.otf", size = 20)
        image.set_default_font("sourcehansans")
        self.disp = display.Display()
        self.disp_w = self.disp.width()
        self.disp_h = self.disp.height()

        self.__show_load_info(f'Init touchscreen..')
        self.ts = touchscreen.TouchScreen()
        self.check_memory()

        self.__show_load_info('Loading sensevoice module..')
        sensevoice_loader = ModuleLoader('maix.sensevoice')
        sensevoice = sensevoice_loader.try_get_module()

        self.__show_load_info(f'Init asr model..')
        self.asr = sensevoice.Sensevoice("/root/models/sensevoice-maixcam2/model.mud", stream=False)
        self.asr.start()
        loader_count = 0
        loader_max_count = 34
        while True:
            if app.need_exit():
                break

            if self.asr.is_ready(block=False):
                break

            time.sleep(1)
            loader_count += 1
            loader_count = loader_count if loader_count < loader_max_count else (loader_max_count - 1)
            self.__show_load_info(f'Init asr model.. {loader_count}/{loader_max_count}', tips='It may wait for a long time.')
        self.__show_load_info(f'Init asr model.. {loader_max_count}/{loader_max_count}', tips='It may wait for a long time.')

        self.__show_load_info(f'Init recorder..')
        self.recorder = audio.Recorder(sample_rate=16000, channel=1, block=False)
        self.recorder.volume(100)
        self.pcm = None
        self.recorder_pcm_buffer:None|bytes = None
        self.img_exit = image.load("./assets/exit.jpg").resize(40, 40)
        self.exit_box = [0, 0, self.img_exit.width(), self.img_exit.height()]
        self.need_exit = False
        self.need_save_pcm = False
        self.title = ''

        self.img_record_str = "Long press me"
        img_record_str_size = image.string_size(self.img_record_str)
        self.img_record_str_box = [(self.disp_w - img_record_str_size.width())//2, self.disp_h - img_record_str_size.height() - 20, img_record_str_size.width(), img_record_str_size.height()]

        self.img_record = image.load("./assets/record.png").resize(96, 96)
        self.img_record_box = [(self.disp_w - self.img_record.width())//2, (self.disp_h - self.img_record.height() - self.img_record_str_box[3] - 30), self.img_record.width(), self.img_record.height()]
        self.first_touch_record = False
        self.first_touch_record_ms = time.ticks_ms()
        self.long_press_record = False

        self.text = 'No text'
        self.text_box = [0, self.exit_box[3] + 20, self.disp_w, self.disp_h]
        self.status = AppStatus.IDLE

    def __show_load_info(self, text: str, tips: str = '', x:int = 0, y:int = 0, color:image.Color=image.COLOR_WHITE):
        if self.disp:
            str_size = image.string_size(text)
            img = image.Image(self.disp_w, self.disp_h, bg=image.COLOR_BLACK)
            if x == 0:
                x = (img.width() - str_size.width()) // 2
            if y == 0:
                y = (img.height() - str_size.height()) // 2
            img.draw_string(x, y, text, color)

            if tips != '':
                tips_str = f"({tips})"
                tips_scale = 0.8
                tips_size = image.string_size(tips_str, scale=tips_scale)
                tips_x = (img.width() - tips_size.width()) // 2
                tips_y = y + str_size.height() + tips_size.height()
                img.draw_string(tips_x, tips_y, tips_str, color, scale=tips_scale)
            self.disp.show(img)

    def check_memory(self):
        from maix import sys
        ok = False
        font = "sourcehansans"
        mem_info = sys.memory_info()
        if "hw_total" in mem_info:
            hw_total = mem_info.get("hw_total", 0)
            print(f"hw_total: {hw_total}({hw_total/1024/1024/1024}G)")
            if hw_total < 4 * 1024 * 1024 * 1024:       # is not 4g version, try release more memory
                ok = False
            else:
                ok = True
        if ok == False:
            img = image.Image(self.disp_w, self.disp_h, bg=image.COLOR_BLACK)
            err_title_msg = "Ops!!!"
            err_msg = "You need the 4GB version of the board to run this application."
            err_exit_msg = "Tap anywhere on the screen to exit."
            img.draw_string(0, 0, err_title_msg, image.COLOR_WHITE, 1, font=font)
            img.draw_string(0, 20, err_msg, image.COLOR_WHITE, 1, font=font)
            img.draw_string(0, 200, err_exit_msg, image.COLOR_WHITE, 0.6, font=font)
            self.disp.show(img)
            while not app.need_exit():
                ts_data = self.ts.read()
                if ts_data[2]:
                    app.set_exit_flag(True)
                time.sleep_ms(100)
            exit(0)

    def check_touch_box(self, t, box:list, oft:int = 0):
        """This method is used for exiting and you normally do not need to modify or call it.
            You usually don't need to modify it.
        """
        if t[2] and t[0] + oft > box[0] and t[0] < box[0] + box[2] + oft and t[1] + oft > box[1] and t[1] < box[1] + box[3] + oft:
            return True
        else:
            return False

    def draw_ui(self):
        img = image.Image(self.disp_w, self.disp_h, image.Format.FMT_RGB888, bg=image.COLOR_BLACK)
        img.draw_image(self.exit_box[0], self.exit_box[1], self.img_exit)
        img.draw_image(self.img_record_box[0], self.img_record_box[1], self.img_record)
        img.draw_string(self.img_record_str_box[0], self.img_record_str_box[1], self.img_record_str, image.COLOR_WHITE)

        img.draw_rect(self.text_box[0],self.text_box[1],self.text_box[2],self.text_box[3],image.COLOR_WHITE, 2)
        img.draw_string(self.text_box[0]+10,self.text_box[1]+10, self.text, image.COLOR_WHITE)
        self.disp.show(img)

    def run(self):
        last_loop_ms = time.ticks_ms()
        while not app.need_exit():
            ts_data = self.ts.read()
            if self.status == AppStatus.RECORDING:
                if self.pcm is None:
                    self.pcm = self.recorder.record(-1)
                else:
                    self.pcm += self.recorder.record(-1)
            elif self.status == AppStatus.TRANSCRIBE:
                self.text = self.asr.refer(audio_data=self.pcm)
                self.pcm = None
                self.status = AppStatus.IDLE
            else:
                pass

            if self.need_exit:
                app.set_exit_flag(True)
                break

            if self.check_touch_box(ts_data, self.exit_box, 20):
                self.need_exit = True

            if self.check_touch_box(ts_data, self.img_record_box, 20):
                if not self.long_press_record:
                    if not self.first_touch_record:
                        self.first_touch_record = True
                        self.first_touch_record_ms = time.ticks_ms()
                    else:
                        if time.ticks_ms() - self.first_touch_record_ms >= 100:
                            self.long_press_record = True
                            self.text = 'Recording..'
                            self.status = AppStatus.RECORDING
            else:
                if self.long_press_record:
                    self.long_press_record = False
                    self.first_touch_record = False
                    self.status = AppStatus.TRANSCRIBE
                    self.text = "Transcribing ..."

            self.draw_ui()

            if time.ticks_ms() - last_loop_ms >= 10:
                last_loop_ms = time.ticks_ms()
            else:
                time.sleep_ms(10)

        if self.asr:
            self.asr.stop()
            self.asr = None

if __name__ == '__main__':
    a = App()
    a.run()
