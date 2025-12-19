from PIL.Image import ID
from maix import camera, time, display, app, image, touchscreen, audio
import importlib, threading
import os

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
    IDLE=0,
    LOAD_ASR=1,
    LOAD_TXT2IMG_MODEL=2,
    RUN_TXT_TO_IMG=3,
    RUN_IMG_TO_IMG=4
    RECORD_AUDIO=5,

class App:
    sta = AppStatus.IDLE
    last_sta = AppStatus.IDLE
    asr = None
    text2img_model = None
    need_exit = False
    def __init__(self, disp:display.Display):
        self.language = 'zh'
        image.load_font("sourcehansans", "/maixapp/share/font/SourceHanSansCN-Regular.otf", size = 20)
        image.set_default_font("sourcehansans")
        self.disp = disp
        self.disp_w = self.disp.width()
        self.disp_h = self.disp.height()
        self.__show_load_info('Loading touchscreen..')
        self.ts = touchscreen.TouchScreen()
        self.cam = camera.Camera(360, 360)

        self.__show_load_info('Loading audio..')
        self.recorder = audio.Recorder(sample_rate=16000, channel=1)

        self.check_memory()

        self.exit_img = image.load('./assets/exit.jpg')
        self.ai_isp = bool(int(app.get_sys_config_kv("npu", "ai_isp", "1")))
        if self.ai_isp is True:
            app.set_sys_config_kv("npu", "ai_isp", "0")

        # load sdv1_5
        if not os.path.exists("/root/models/lcm-lora-sdv1-5-maixcam2/ax620e_models"):
            self.show_error("You need install lcm-lora-sdv1-5-maixcam2 model from https://huggingface.co/sipeed/lcm-lora-sdv1-5-maixcam2")
            exit(0)

        self.__show_load_info('Loading sdv1_5 module..')
        sdv1_5_loader = ModuleLoader('maix.sdv1_5')
        sdv1_5 = None
        loader_count = 0
        loader_max_count = 56
        while True:
            if app.need_exit():
                break

            sdv1_5 = sdv1_5_loader.try_get_module(block=False)
            if sdv1_5 is not None:
                break

            time.sleep(1)
            loader_count += 1
            loader_count = loader_count if loader_count < loader_max_count else (loader_max_count - 1)
            self.__show_load_info(f'Loading sdv1_5 model.. {loader_count}/{loader_max_count}', tips='It may wait for a long time.')
        self.__show_load_info(f'Loading sdv1_5 model.. {loader_max_count}/{loader_max_count}', tips='It may wait for a long time.')

        # from sdv1_5 import SDV1_5
        self.__show_load_info('Init sdv1_5 model..', tips='It may wait for a long time.')
        self.text2img_model = sdv1_5.SDV1_5("/root/models/lcm-lora-sdv1-5-maixcam2/ax620e_models")
        self.text2img_model.init(img2img=True)

        # load asr model
        self.__show_load_info('Loading sensevoice module..')
        sensevoice_loader = ModuleLoader('maix.sensevoice')
        sensevoice = sensevoice_loader.try_get_module()

        self.__show_load_info('Init asr model..')
        self.asr = sensevoice.Sensevoice("/root/models/sensevoice-maixcam2/model.mud", stream=False)
        self.asr.start()
        loader_count = 0
        loader_max_count = 8
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
        self.set_sta(AppStatus.IDLE)

    def set_sta(self, new_status):
        if self.sta != new_status:
            self.last_sta = self.sta
            self.sta = new_status

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

    def show_exit(self):
        print('Show exit..')
        if self.disp:
            img = image.Image(self.disp_w, self.disp_h, bg=image.COLOR_BLACK)
            exit_str = "Exit.."
            exit_str_size = image.string_size(exit_str)
            img.draw_string((img.width() - exit_str_size.width())//2, (img.height() - exit_str_size.height())//2 , exit_str, image.COLOR_WHITE)
            self.disp.show(img)
        else:
            print('display is None')

    def show_error(self, err_msg:str):
        img = image.Image(self.disp_w, self.disp_h, bg=image.COLOR_BLACK)
        err_title = "Oops, there's a problem!"
        err_title_scale = 1.5
        err_title_size = image.string_size(err_title, scale=err_title_scale)
        err_title_x = 0
        err_title_y = err_title_size.height()
        img.draw_string(err_title_x, err_title_y, err_title, image.COLOR_WHITE, scale=err_title_scale)

        err_msg_scale = 1.5
        err_msg_size = image.string_size(err_msg, scale=err_msg_scale)
        img.draw_string(0, err_title_y + err_title_size.height() + err_msg_size.height(), err_msg, image.COLOR_WHITE, scale=err_msg_scale)
        self.disp.show(img)
        while not app.need_exit():
            time.sleep_ms(100)

    def check_exit(self):
        ts_data = self.ts.read()
        exit_img_x = 0
        exit_img_y = 0
        exit_img_w = self.exit_img.width()*8
        exit_img_h = self.exit_img.height()*8
        if ts_data[2] and 0<=ts_data[0]<=exit_img_w + exit_img_x and 0 <=ts_data[1]<=exit_img_h + exit_img_y:
            return True
        else:
            return False

    def show_ui(self):
        img_w = self.cam.width()
        img_h = self.cam.height()
        img_box = [0, 0, img_w, img_h]
        prompt_img = image.Image(img_w, img_h, bg=image.COLOR_BLACK)

        text_box = [0, img_box[3], self.disp_w, self.disp_h - img_box[3]]
        text = 'No text'
        prompt = ''

        btn_count = 4
        btn_width = self.disp_w - img_box[2]
        btn_height = img_h // btn_count
        record_str = "Record (Long press)"
        record_str_size = image.string_size(record_str)
        record_btn_box = [0, 0, btn_width, btn_height]
        record_btn_box[0] = img_box[2]
        record_btn_box[1] = btn_height * 0

        text_to_img_str = "Text To Image"
        text_to_img_size = image.string_size(text_to_img_str)
        text_to_img_box = [0, 0, btn_width, btn_height]
        text_to_img_box[0] = img_box[2]
        text_to_img_box[1] = btn_height * 1

        img_to_img_str = "Image To Image"
        img_to_img_size = image.string_size(img_to_img_str)
        img_to_img_box = [0, 0, btn_width, btn_height]
        img_to_img_box[0] = img_box[2]
        img_to_img_box[1] = btn_height * 2

        camera_str = "Camera"
        camera_size = image.string_size(camera_str)
        camera_box = [0, 0, btn_width // 2, btn_height]
        camera_box[0] = img_box[2]
        camera_box[1] = btn_height * 3

        capture_str = "Capture"
        capture_size = image.string_size(capture_str)
        capture_box = [0, 0, btn_width // 2, btn_height]
        capture_box[0] = img_box[2] + btn_width // 2
        capture_box[1] = btn_height * 3

        save_text2img_path = '/tmp/text2img.jpg'
        pcm = None
        class Status:
            IDLE=0,
            RECORDING=1,
            TRANSCRIBING=2,
            RUN_TXT_TO_IMG=3,
            RUN_IMG_TO_IMG=4,
            RUN_CAMERA=5,
            RUN_CAPTURE=6,
        status = Status.IDLE

        first_press_reocrd_ms = time.ticks_ms()
        first_press_reocrd = False
        long_press_record = False
        long_press_ms = 100

        cam_img = None
        show_img = None
        while not self.need_exit:
            img = image.Image(self.disp_w, self.disp_h, bg=image.COLOR_BLACK)

            ts_data = self.ts.read()

            if status == Status.RECORDING:
                if pcm is None:
                    pcm = self.recorder.record(-1)
                else:
                    pcm += self.recorder.record(-1)
            elif status == Status.TRANSCRIBING:
                prompt = self.asr.refer(audio_data=pcm)
                text = prompt
                status = Status.IDLE
                print(text)
            elif status == Status.RUN_TXT_TO_IMG:
                self.text2img_model.refer(prompt=prompt, save_path=save_text2img_path)
                prompt_img = image.load(save_text2img_path).resize(img_w, img_h)
                text = 'text to image complete, prompt:\n' + prompt
                show_img = prompt_img
                status = Status.IDLE
            elif status == Status.RUN_IMG_TO_IMG:
                save_path = "/tmp/img2img.jpg"
                self.text2img_model.refer(prompt=prompt, init_image_path=save_text2img_path, seed=1, save_path=save_path)
                prompt_img = image.load(save_path).resize(img_w, img_h)
                text = 'image to image complete, prompt:\n' + prompt
                show_img = prompt_img
                status = Status.IDLE
            elif status == Status.RUN_CAMERA:
                cam_img = self.cam.read()
                show_img = cam_img
            elif status == Status.RUN_CAPTURE:
                if cam_img:
                    prompt_img = cam_img
                    prompt_img.save(save_text2img_path)
                    show_img = prompt_img
                    cam_img = None
                status = Status.IDLE
            else:
                pass

            if ts_data[2] and record_btn_box[0]<=ts_data[0]<=record_btn_box[0] + record_btn_box[2] and record_btn_box[1] <=ts_data[1]<=record_btn_box[1] + record_btn_box[3]:
                if long_press_record is False:
                    if not first_press_reocrd:
                        first_press_reocrd = True
                        first_press_reocrd_ms = time.ticks_ms()
                    else:
                        if time.ticks_ms() - first_press_reocrd_ms >= long_press_ms:
                            long_press_record = True
                            text = f'Recording..'
                            pcm = None
                            print(text)
                            status = Status.RECORDING
            else:
                if long_press_record:
                    long_press_record = False
                    first_press_reocrd = False
                    status = Status.TRANSCRIBING
                    text = f"Transcribing ..."
                    print(text)

            if ts_data[2] and text_to_img_box[0]<=ts_data[0]<=text_to_img_box[0] + text_to_img_box[2] and text_to_img_box[1] <=ts_data[1]<=text_to_img_box[1] + text_to_img_box[3]:
                if prompt == '':
                    status = Status.IDLE
                    text = 'Click record to get the prompt\n'
                else:
                    status = Status.RUN_TXT_TO_IMG
                    text = 'run text to image, prompt:\n' + prompt
                print("touch text to image")

            if ts_data[2] and img_to_img_box[0]<=ts_data[0]<=img_to_img_box[0] + img_to_img_box[2] and img_to_img_box[1] <=ts_data[1]<=img_to_img_box[1] + img_to_img_box[3]:
                if prompt == '':
                    status = Status.IDLE
                    text = 'Click record to get the prompt\n'
                elif not os.path.exists(save_text2img_path):
                    status = Status.IDLE
                    text = 'Click text to img to get the image\n'
                else:
                    status = Status.RUN_IMG_TO_IMG
                    text = 'run image to image, prompt:\n' + prompt
                print("touch image to image")

            if ts_data[2] and camera_box[0]<=ts_data[0]<=camera_box[0] + camera_box[2] and camera_box[1] <=ts_data[1]<=camera_box[1] + camera_box[3]:
                if status == Status.RUN_CAMERA:
                    print('stop camera')
                    show_img = prompt_img
                    status = Status.IDLE
                else:
                    print('start camera')
                    status = Status.RUN_CAMERA
                time.sleep_ms(200)

            if ts_data[2] and capture_box[0]<=ts_data[0]<=capture_box[0] + capture_box[2] and capture_box[1] <=ts_data[1]<=capture_box[1] + capture_box[3]:
                print('capture')
                status = Status.RUN_CAPTURE

            img.clear()
            if show_img:
                img.draw_image(0, 0, show_img)

            img.draw_string(record_btn_box[0] + (record_btn_box[2] - record_str_size.width())//2, record_btn_box[1] + (record_btn_box[3]- record_str_size.height())//2, record_str, image.COLOR_WHITE)
            img.draw_rect(record_btn_box[0], record_btn_box[1], record_btn_box[2], record_btn_box[3], image.COLOR_WHITE, 2)

            img.draw_string(text_to_img_box[0] + (text_to_img_box[2] - text_to_img_size.width())//2, text_to_img_box[1] + (text_to_img_box[3]- text_to_img_size.height())//2, text_to_img_str, image.COLOR_WHITE)
            img.draw_rect(text_to_img_box[0], text_to_img_box[1], text_to_img_box[2], text_to_img_box[3], image.COLOR_WHITE, 2)

            img.draw_string(img_to_img_box[0] + (img_to_img_box[2] - img_to_img_size.width())//2, img_to_img_box[1] + (img_to_img_box[3]- img_to_img_size.height())//2, img_to_img_str, image.COLOR_WHITE)
            img.draw_rect(img_to_img_box[0], img_to_img_box[1], img_to_img_box[2], img_to_img_box[3], image.COLOR_WHITE, 2)

            img.draw_string(camera_box[0] + (capture_box[2] - camera_size.width())//2, camera_box[1] + (camera_box[3]- camera_size.height())//2, camera_str, image.COLOR_WHITE)
            img.draw_rect(camera_box[0], camera_box[1], camera_box[2], camera_box[3], image.COLOR_WHITE, 2)

            img.draw_string(capture_box[0] + (capture_box[2] - capture_size.width())//2, capture_box[1] + (capture_box[3]- capture_size.height())//2, capture_str, image.COLOR_WHITE)
            img.draw_rect(capture_box[0], capture_box[1], capture_box[2], capture_box[3], image.COLOR_WHITE, 2)

            img.draw_rect(text_box[0], text_box[1], text_box[2], text_box[3], image.COLOR_WHITE, 2)
            img.draw_string(text_box[0]+10, text_box[1]+10, text, image.COLOR_WHITE)

            # exit img
            img.draw_image(0, 0, self.exit_img)
            if self.check_exit():
                self.need_exit = True
                self.show_exit()
                break

            if app.need_exit():
                self.need_exit = True
                self.show_exit()
                break

            self.disp.show(img)
            time.sleep_ms(50)

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

    def run(self):
        while not self.need_exit:
            self.show_ui()

        self.show_exit()

        if self.asr:
            self.asr.stop()
            del self.asr
            self.asr = None

        if self.text2img_model:
            del self.text2img_model
            self.text2img_model = None

        if self.cam:
            del self.cam
            self.cam = None

        if self.disp:
            del self.disp
            self.disp = None

        app.set_exit_flag(True)
        app.set_sys_config_kv("npu", "ai_isp", "1" if self.ai_isp else "0")

if __name__ == '__main__':
    disp = display.Display()
    try:
        appication = App(disp)
        appication.run()
    except Exception:
        import traceback
        msg = traceback.format_exc()
        print(msg)
        img = image.Image(disp.width(), disp.height(), bg=image.COLOR_BLACK)
        img.draw_string(0, 0, msg, image.COLOR_WHITE)
        disp.show(img)
        while not app.need_exit():
            time.sleep_ms(100)
