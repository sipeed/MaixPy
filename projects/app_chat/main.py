
from maix import nn, audio, time, display, app, image, touchscreen
import threading
from queue import Queue, Empty
import re

class App:
    def __init__(self):
        image.load_font("sourcehansans", "/maixapp/share/font/SourceHanSansCN-Regular.otf", size = 20)
        image.set_default_font("sourcehansans")
        self.disp = display.Display()
        self.disp_w = 320
        self.disp_h = 240
        self.__show_load_info('loading touchscreen..')
        self.ts = touchscreen.TouchScreen()

        self.exit_img = image.load('./assets/exit.jpg')
        # self.__show_load_info('loading key..')
        # self.key_obj = key.Key(self.on_key)
        # self.key_status = False

        self.__show_load_info('loading recorder..')
        self.default_wav_path = "/root/audio.wav"
        self.default_record_samplerate = 16000
        self.default_record_volume = 70
        self.recorder = audio.Recorder(sample_rate=self.default_record_samplerate)
        self.recorder.volume(self.default_record_volume)

        self.__show_load_info("loading webrtcvad..")
        try:
            import webrtcvad
            self.vad = webrtcvad.Vad()
            self.vad.set_mode(3)
            self.vad_duration_ms = 30
        except:
            self.vad = None

        self.__show_load_info('loading player..')
        self.player = audio.Player(sample_rate=44100)
        self.player.volume(50)
        self.player_queue = Queue(100)
        self.player_thread = threading.Thread(target=self.player_thread_handle, daemon=True)
        self.player_thread.start()

        self.__show_load_info('loading whisper..')
        ai_isp_on = bool(int(app.get_sys_config_kv("npu", "ai_isp", "1")))
        if ai_isp_on is True:
            img = image.Image(320, 240, bg=image.COLOR_BLACK)
            err_msg = "You need edit /boot/configs to set ai_isp_on to 0"
            err_msg_size = image.string_size(err_msg)
            img.draw_string((img.width() - err_msg_size.width()) // 2, (img.height() - err_msg_size.height()) // 2, err_msg, image.COLOR_RED)
            self.disp.show(img)
            while not app.need_exit():
                ts_data = self.ts.read()
                if ts_data[2]:
                    app.set_exit_flag(True)
                time.sleep_ms(100)
        self.whisper = nn.Whisper(model="/root/models/whisper-base/whisper-base.mud", language="en")

        self.__show_load_info('loading llm..')
        # /root/models/Qwen2.5-0.5B-Instruct/model.mud
        # /root/models/Qwen2.5-1.5B-Instruct/model.mud
        self.llm = nn.Qwen("/root/models/Qwen2.5-1.5B-Instruct/model.mud")
        self.llm.set_system_prompt("You are Qwen, created by Alibaba Cloud. You are a helpful assistant.")
        self.llm.set_reply_callback(self.__llm_on_reply)
        self.llm_last_msg = ""

        self.__show_load_info('loading melotts..')
        self.tts = nn.MeloTTS(model="/root/models/melotts/melotts-zh.mud", speed = 0.8, language='en')

        self.tts_queue = Queue(100)
        self.tts_thread = threading.Thread(target=self.tts_thread_handle, daemon=True)
        self.tts_thread.start()

    def player_thread_handle(self):
        while not app.need_exit():
            try:
                pcm = self.player_queue.get(timeout=500)
                print('play start')
                t = time.ticks_ms()
                self.player.play(pcm)
                print('player cost', time.ticks_ms() - t)
                print('play finish')
            except Empty:
                continue

    def tts_thread_handle(self):
        while not app.need_exit():
            try:
                msg = self.tts_queue.get(timeout=500)
                print('tts queue get:', msg)
                t = time.ticks_ms()
                pcm = self.tts.infer(msg, output_pcm=True)
                print('tts infer cost', time.ticks_ms() - t)
                self.player_queue.put(pcm)
            except Empty:
                continue

    def __llm_on_reply(self, obj, resp):
        print(resp.msg_new, end="")
        img = image.Image(320, 240, bg=image.COLOR_BLACK)
        self.__draw_string_upper_center(img, text="Run LLM..", color=image.COLOR_GREEN)
        # img.draw_string(0, 0, "Run LLM..", image.COLOR_GREEN)
        img.draw_string(0, 30, resp.msg, image.COLOR_WHITE)
        self.disp.show(img)

        self.llm_last_msg += resp.msg_new
        parts=re.split(r"[,.!?]", self.llm_last_msg)
        # print('parts', parts)
        if len(parts) > 1:
            if "!" in self.llm_last_msg:
                push_msg = parts[0] + "!"
            elif "," in self.llm_last_msg:
                push_msg = parts[0] + ","
            elif "." in self.llm_last_msg:
                push_msg = parts[0] + "."
            elif "?" in self.llm_last_msg:
                push_msg = parts[0] + "?"
            else:
                push_msg = parts[0]
                pass
            self.llm_last_msg = parts[-1]
            self.tts_queue.put(push_msg)

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

    def __reset_recorder(self, save_file: bool):
        if self.recorder:
            del self.recorder
        if save_file:
            self.recorder = audio.Recorder(self.default_wav_path, self.default_record_samplerate)
        else:
            self.recorder = audio.Recorder(sample_rate=self.default_record_samplerate)
        self.recorder.volume(self.default_record_volume)

    def run(self):
        class Status:
            IDLE=0
            SPEAKING=1
            TRANSCRIBE=2
            TTS=3
            LLM=4
            VAD=5
        status = Status.IDLE
        record_ms = 4000
        asr_result = None
        llm_result = None
        start_vad = False

        while not app.need_exit():
            img = image.Image(320, 240, bg=image.COLOR_BLACK)

            ts_data = self.ts.read()
            if status == Status.VAD:
                self.__draw_string_upper_center(img, text="VAD..", color=image.COLOR_GREEN)
                # img.draw_string(0, 0, "VAD..", image.COLOR_GREEN)
            elif status == Status.SPEAKING:
                self.__draw_string_upper_center(img, text="Speaking..", color=image.COLOR_GREEN)
                # img.draw_string(0, 0, "Speaking..", image.COLOR_GREEN)
            elif status == Status.TRANSCRIBE:
                self.__draw_string_upper_center(img, text="Transcribing..", color=image.COLOR_GREEN)
                # img.draw_string(0, 0, "Transcribing..", image.COLOR_GREEN)
            elif status == Status.LLM:
                self.__draw_string_upper_center(img, text="Run LLM..", color=image.COLOR_GREEN)
                # img.draw_string(0, 0, "Run LLM..", image.COLOR_GREEN)
                if asr_result:
                    img.draw_string(0, 30, asr_result, image.COLOR_WHITE)
                elif llm_result:
                    img.draw_string(0, 30, llm_result, image.COLOR_WHITE)
            elif status == Status.TTS:
                self.__draw_string_upper_center(img, text="Run MelloTTS..", color=image.COLOR_GREEN)
                # img.draw_string(0, 0, "Run MelloTTS..", image.COLOR_GREEN)
                if asr_result:
                    img.draw_string(0, 30, asr_result, image.COLOR_WHITE)
                elif llm_result:
                    img.draw_string(0, 30, llm_result, image.COLOR_WHITE)
            else:
                # img.draw_string(0, 0, "Waiting press touchscreen..", image.COLOR_GREEN)
                self.__draw_string_upper_center(img, text="Waiting press touchscreen..", color=image.COLOR_GREEN)
                if asr_result:
                    img.draw_string(0, 30, asr_result, image.COLOR_WHITE)
                elif llm_result:
                    img.draw_string(0, 30, llm_result, image.COLOR_WHITE)

            exit_img_x = 0
            exit_img_y = 0
            img.draw_image(exit_img_x, exit_img_y, self.exit_img)
            if ts_data[2] and 0<=ts_data[0]<=self.exit_img.width() + exit_img_x*2 and 0 <=ts_data[1]<=self.exit_img.height() + exit_img_y*2:
                print('exit')
                app.set_exit_flag(True)
            self.disp.show(img)

            if status == Status.IDLE:                
                if ts_data[2]:
                    if self.vad:
                        start_vad = not start_vad
                        status = Status.VAD
                    else:
                        status = Status.SPEAKING
            elif status == Status.VAD:
                if self.vad:
                    if start_vad:
                        pcm = self.recorder.record(self.vad_duration_ms)
                        if pcm and len(pcm) > 0:
                            is_speech = self.vad.is_speech(pcm, self.default_record_samplerate)
                            if is_speech:
                                start_vad = False
                                status = Status.SPEAKING
                else:
                    status = Status.SPEAKING
            elif status == Status.SPEAKING:
                self.__reset_recorder(True)
                self.recorder.record(record_ms)
                self.recorder.finish()
                self.__reset_recorder(False)
                status = Status.TRANSCRIBE
            elif status == Status.TRANSCRIBE:
                asr_result = self.whisper.transcribe(self.default_wav_path)
                print(asr_result)
                status = Status.LLM
            elif status == Status.LLM:
                if asr_result:
                    llm_result0 = self.llm.send(asr_result)
                    llm_result = llm_result0.msg
                    self.llm.clear_context()
                    print(llm_result)
                    status = Status.TTS
                    asr_result = None
            elif status == Status.TTS:
                if self.tts_queue.empty():
                    status = Status.IDLE
            else:
                status = Status.IDLE
            time.sleep_ms(5)

if __name__ == '__main__':
    appication = App()
    appication.run()