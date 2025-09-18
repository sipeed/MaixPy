from maix import nn, camera, time, display, app, image, touchscreen
import threading

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
    class Status:
        IDLE=0,
        VLM_START=1,
        VLM_RUNNING=2,
        VLM_STOP=3

    def __init__(self):
        image.load_font("sourcehansans", "/maixapp/share/font/SourceHanSansCN-Regular.otf", size = 20)
        image.set_default_font("sourcehansans")
        self.disp = display.Display()
        self.disp_w = self.disp.width()
        self.disp_h = self.disp.height()
        self.__show_load_info('loading touchscreen..')
        self.ts = touchscreen.TouchScreen()

        self.cam = camera.Camera(640, 360)

        self.exit_img = image.load('./assets/exit.jpg')
        ai_isp_on = bool(int(app.get_sys_config_kv("npu", "ai_isp", "1")))
        if ai_isp_on is True:
            img = image.Image(self.disp_w, self.disp_h, bg=image.COLOR_BLACK)
            err_msg = "Please trun off AI ISP first via the Settings app(Settings->AI ISP)"
            img.draw_string(0, 0, err_msg, image.COLOR_RED)
            self.disp.show(img)
            while not app.need_exit():
                ts_data = self.ts.read()
                if ts_data[2]:
                    app.set_exit_flag(True)
                time.sleep_ms(100)

        self.__show_load_info('loading vlm..')
        self.vlm = nn.InternVL('/root/models/InternVL2.5-1B/model.mud')
        self.vlm_in_w = self.vlm.input_width()
        self.vlm_in_h = self.vlm.input_height()
        self.vlm_in_fmt = self.vlm.input_format()
        self.vlm.set_system_prompt("你是由上海人工智能实验室联合商汤科技开发的书生多模态大模型, 英文名叫InternVL, 是一个有用无害的人工智能助手。")
        self.vlm.set_reply_callback(self.__vlm_on_reply)
        self.vlm_img: image.Image | None = None
        self.vlm_thread_lock = threading.Lock()
        self.vlm_result:str = ''
        self.page_text = PagedText(self.disp_w, self.disp_h - self.cam.height())

        self.sta = self.Status.IDLE

    def __vlm_thread(self, vlm, img:image.Image, msg: str):
        vlm.set_image(img, image.Fit.FIT_CONTAIN)
        resp = vlm.send(msg)
        print(resp)
        with self.vlm_thread_lock:
            self.sta = self.Status.VLM_STOP

    def run_vlm(self, img: image.Image, msg: str):
        self.page_text.clear()
        t = threading.Thread(target=self.__vlm_thread, args=[self.vlm, img, msg], daemon=True)
        t.start()
        # t.run()

    def show_ui(self):
        img = image.Image(self.disp_w, self.disp_h, bg=image.COLOR_BLACK)
        ts_data = self.ts.read()
        if self.vlm_img:
            # vlm img
            img.draw_image(0, 0, self.vlm_img)
            text_img_x = 0
            text_img_y = self.cam.height()
            text_img = image.Image(self.disp_w, self.disp_h - self.cam.height(), bg=image.COLOR_BLACK)

            # msg img
            self.page_text.draw_last_page_on(text_img, image.COLOR_WHITE)
            img.draw_image(text_img_x, text_img_y, text_img)
        else:
            text_img_x = 0
            text_img_y = self.cam.height()
            text_img = image.Image(self.disp_w, self.disp_h - self.cam.height(), bg=image.COLOR_BLACK)
            text_img.draw_string(0, 0, "running..", image.COLOR_WHITE)
            img.draw_image(text_img_x, text_img_y, text_img)

        # exit img
        exit_img_x = 0
        exit_img_y = 0
        img.draw_image(exit_img_x, exit_img_y, self.exit_img)

        if ts_data[2] and 0<=ts_data[0]<=self.exit_img.width() + exit_img_x*2 and 0 <=ts_data[1]<=self.exit_img.height() + exit_img_y*2:
            print('exit')
            app.set_exit_flag(True)

        self.disp.show(img)


    def __vlm_on_reply(self, obj, resp):
        print(resp.msg_new)
        if self.vlm_img:
            self.page_text.add_text(resp.msg_new)
        # self.show_ui()

    def __show_load_info(self, text: str, x:int = 0, y:int = 0, color:image.Color=image.COLOR_WHITE):
        if self.disp:
            str_size = image.string_size(text)
            img = image.Image(self.disp_w, self.disp_h, bg=image.COLOR_BLACK)
            if x == 0:
                x = (img.width() - str_size.width()) // 2
            if y == 0:
                y = (img.height() - str_size.height()) // 2
            img.draw_string(x, y, text, image.COLOR_WHITE)
            self.disp.show(img)

    def __draw_string_upper_center(self, img, y:int=8, text:str="", color:image.Color=image.COLOR_WHITE):
        x = 0
        text_size = image.string_size(text)
        x = (img.width() - text_size.width()) // 2
        img.draw_string(x, y, text, color)

    def run(self):
        while not app.need_exit():
            with self.vlm_thread_lock:
                sta = self.sta

            if sta == self.Status.IDLE:
                print('IDLE')
                self.vlm_img = self.cam.read()
                if self.vlm_img:
                    with self.vlm_thread_lock:
                        self.sta = self.Status.VLM_START
            elif sta == self.Status.VLM_START:
                print('VLM_START')
                if self.vlm_img:
                    self.run_vlm(self.vlm_img, 'Describe the picture')
                    with self.vlm_thread_lock:
                        self.sta = self.Status.VLM_RUNNING
            elif sta == self.Status.VLM_RUNNING:
                print('VLM_RUNNING')
                self.vlm_img = self.cam.read()
            elif sta == self.Status.VLM_STOP:
                print('VLM_STOP')
                with self.vlm_thread_lock:
                    self.sta = self.Status.IDLE

            self.show_ui()

if __name__ == '__main__':
    appication = App()
    appication.run()