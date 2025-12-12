from maix import nn, audio, time, display, app, image, touchscreen
import importlib, threading
import re

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

class PagedText:
    def __init__(self, page_width = -1, page_height = -1):
        """
        page_width: 每页宽度
        page_height: 每页最大行数
        char_width_func: 一个函数, 输入字符返回宽度 (例如 lambda c: 1 或字典映射)
        """
        self.page_width = page_width
        self.page_height = page_height
        self.pages = [[]]  # 每个元素是 page, page 是行的列表, 行是 (text, width)

    def reset(self, page_width, page_height):
        self.page_width = page_width
        self.page_height = page_height
        self.pages = [[]]

    def add_text(self, text):
        current_page = self.pages[-1]
        if not current_page:
            current_page.append(("", 0, 0))  # 初始化第一行

        page_height_used = sum(line[2] for line in current_page)
        
        for ch in text:
            line_text, _, line_h = current_page[-1]
            new_line_text = line_text + ch
            size = image.string_size(new_line_text)
            ch_w = size[0]
            ch_h = size[1]
    
            # 尝试放到当前行
            if ch_w <= self.page_width:
                # 更新行
                new_w = ch_w
                new_h = max(line_h, ch_h)
                # 替换行
                current_page[-1] = (new_line_text, new_w, new_h)
            else:
                # 需要换行
                if page_height_used + line_h <= self.page_height:
                    current_page.append((ch, ch_w, ch_h))
                    page_height_used += line_h  # 累加上一行高度
                else:
                    # 需要换页
                    self.pages.append([(ch, ch_w, ch_h)])
                    current_page = self.pages[-1]
                    page_height_used = ch_h

            page_height_used = sum(line[2] for line in current_page)
            # print("OVER", line_text, line_w, line_h, page_height_used)

    def clear(self):
        self.pages = [[]]

    def print(self):
        for i, page in enumerate(self.pages):
            print(f"Page {i+1}:")
            page_height = sum(line[2] for line in page)
            for line_text, line_width, line_height in page:
                print(f"  '{line_text}' (w={line_width}, h={line_height})")
            print(f"  -> total height used = {page_height}")
            print()

    def draw_last_page_on(self, img:image.Image, color: image.Color = image.COLOR_WHITE):
        if img.width() != self.page_width or img.height() != self.page_height:
            return

        current_page = self.pages[-1]
        if not current_page:
            return

        height = 0
        for line_text, _, line_height in current_page:
            img.draw_string(0, height, line_text, color, wrap_space=0)            
            height += line_height

class App:
    def __init__(self):
        image.load_font("sourcehansans", "/maixapp/share/font/SourceHanSansCN-Regular.otf", size = 20)
        image.set_default_font("sourcehansans")
        self.disp = display.Display()
        self.disp_w = self.disp.width()
        self.disp_h = self.disp.height()
        self.__show_load_info('Loading touchscreen..')
        self.ts = touchscreen.TouchScreen()

        self.check_memory()

        self.img_exit = image.load("./assets/exit.jpg").resize(40, 40)
        self.exit_box = [0, 0, self.img_exit.width(), self.img_exit.height()]

        self.__show_load_info('Loading recorder..')
        self.default_wav_path = "/root/audio.wav"
        self.default_record_samplerate = 16000
        self.default_record_volume = 70
        self.recorder = audio.Recorder(sample_rate=self.default_record_samplerate)
        self.recorder.volume(self.default_record_volume)

        self.__show_load_info('Check ai isp..')
        ai_isp_on = bool(int(app.get_sys_config_kv("npu", "ai_isp", "1")))
        if ai_isp_on is True:
            img = image.Image(320, 240, bg=image.COLOR_BLACK)
            err_title_msg = "Ops!!!"
            err_msg = "You need open the Settings app, find the AI ISP option, and select Off."
            err_exit_msg = "Tap anywhere on the screen to exit."
            img.draw_string(0, 0, err_title_msg, image.COLOR_WHITE, 0.8)
            img.draw_string(0, 20, err_msg, image.COLOR_WHITE, 0.8)
            img.draw_string(0, 200, err_exit_msg, image.COLOR_WHITE, 0.6)
            self.disp.show(img)
            while not app.need_exit():
                ts_data = self.ts.read()
                if ts_data[2]:
                    app.set_exit_flag(True)
                time.sleep_ms(100)
            exit(0)

        self.__show_load_info('Loading sensevoice module..')
        sensevoice_loader = ModuleLoader('maix.sensevoice')
        sensevoice = sensevoice_loader.try_get_module()

        self.__show_load_info(f'Init asr model..')
        self.asr = sensevoice.Sensevoice("/root/models/sensevoice-maixcam2/model.mud", stream=False)
        self.asr.start()
        self.pcm = None
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

        self.__show_load_info('Loading llm..', tips='It may wait for a long time.')
        # /root/models/Qwen2.5-0.5B-Instruct/model.mud
        # /root/models/Qwen2.5-1.5B-Instruct/model.mud
        self.llm = nn.Qwen("/root/models/Qwen2.5-0.5B-Instruct/model.mud")
        self.llm.set_system_prompt("You are Qwen, created by Alibaba Cloud. You are a helpful assistant.")
        self.llm.set_reply_callback(self.__llm_on_reply)
        self.llm_last_msg = ""

        self.page_text = PagedText()

        self.img_record_str = "Long press me"
        img_record_str_size = image.string_size(self.img_record_str)
        self.img_record_str_box = [(self.disp_w - img_record_str_size.width())//2, self.disp_h - img_record_str_size.height() - 20, img_record_str_size.width(), img_record_str_size.height()]

        self.img_record = image.load("./assets/record.png").resize(96, 96)
        self.img_record_box = [(self.disp_w - self.img_record.width())//2, (self.disp_h - self.img_record.height() - self.img_record_str_box[3] - 30), self.img_record.width(), self.img_record.height()]
        self.first_touch_record = False
        self.first_touch_record_ms = time.ticks_ms()
        self.long_press_record = False

        self.prompt = 'No text'
        self.text_box = [0, self.exit_box[3] + 20, self.disp_w, self.disp_h]

    def check_touch_box(self, t, box:list, oft:int = 0):
        """This method is used for exiting and you normally do not need to modify or call it.
            You usually don't need to modify it.
        """
        if t[2] and t[0] + oft > box[0] and t[0] < box[0] + box[2] + oft and t[1] + oft > box[1] and t[1] < box[1] + box[3] + oft:
            return True
        else:
            return False

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


    def __llm_on_reply(self, obj, resp):
        print(resp.msg_new, end="")
        ts_data = self.ts.read()
        self.show_ui()

        if self.check_touch_box(ts_data, self.exit_box, 20):
            app.set_exit_flag(True)

        self.llm_last_msg += resp.msg_new

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

    def show_ui(self):
        img = image.Image(self.disp_w, self.disp_h, bg=image.COLOR_BLACK)
        img.draw_image(self.exit_box[0], self.exit_box[1], self.img_exit)
        img.draw_image(self.img_record_box[0], self.img_record_box[1], self.img_record)
        img.draw_string(self.img_record_str_box[0], self.img_record_str_box[1], self.img_record_str, image.COLOR_WHITE)

        img.draw_rect(self.text_box[0],self.text_box[1],self.text_box[2],self.text_box[3],image.COLOR_WHITE, 2)

        text = self.prompt + '\n' + self.llm_last_msg
        img.draw_string(self.text_box[0]+10,self.text_box[1]+10, text, image.COLOR_WHITE, scale=1.2)
        self.disp.show(img)

    def run(self):
        class Status:
            IDLE=0
            RECORDING=1
            TRANSCRIBE=2
            TTS=3
            LLM=4
            VAD=5
        status = Status.IDLE

        while not app.need_exit():
            ts_data = self.ts.read()
            if status == Status.RECORDING:
                if self.pcm is None:
                    self.pcm = self.recorder.record(-1)
                else:
                    self.pcm += self.recorder.record(-1)
            elif status == Status.TRANSCRIBE:
                self.prompt = self.asr.refer(audio_data=self.pcm)
                print('transcribe:', self.prompt)
                self.pcm = None
                status = Status.LLM
            elif status == Status.LLM:
                self.llm_last_msg = ''
                llm_result0 = self.llm.send(self.prompt)
                if llm_result0:
                    self.llm.clear_context()
                    print("llm_result0:", llm_result0)
                status = Status.IDLE
            else:
                pass

            if self.check_touch_box(ts_data, self.exit_box, 20):
                app.set_exit_flag(True)

            if self.check_touch_box(ts_data, self.img_record_box, 20):
                if not self.long_press_record:
                    if not self.first_touch_record:
                        self.first_touch_record = True
                        self.first_touch_record_ms = time.ticks_ms()
                    else:
                        if time.ticks_ms() - self.first_touch_record_ms >= 100:
                            self.long_press_record = True
                            self.prompt = 'Recording..'
                            status = Status.RECORDING
            else:
                if self.long_press_record:
                    self.long_press_record = False
                    self.first_touch_record = False
                    status = Status.TRANSCRIBE
                    self.prompt = "Transcribing ..."

            self.show_ui()
            
            time.sleep_ms(5)
        
        if self.llm:
            del self.llm
            self.llm = None

        if self.asr:
            self.asr.stop()
            self.asr = None

if __name__ == '__main__':
    appication = App()
    appication.run()