from maix import display, nn, touchscreen, app, image, time, audio
import webrtcvad
import threading
import os

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

        self.ts = touchscreen.TouchScreen()
        self.asr = nn.Whisper(model="/root/models/whisper-base/whisper-base.mud", language=self.language)
        self.asr_result:None|str = None
        self.asr_thread:None|threading.Thread = None
        self.asr_thread_exit:bool = False
        self.asr_thread_lock = threading.Lock()

        self.vad = webrtcvad.Vad()
        self.vad.set_mode(3)
        self.vad_duration_ms = 30

        self.recorder = audio.Recorder('/tmp/record.wav', sample_rate=16000, channel=1, block=False)
        self.recorder.volume(60)
        self.recorder_pcm_buffer:None|bytes = None
        self.img_exit = image.load("./assets/exit.jpg").resize(40, 40)
        self.exit_box = [0, 0, self.img_exit.width(), self.img_exit.height()]
        self.need_exit = False
        self.need_save_pcm = False
        self.title = ''

        btn_color = image.Color.from_rgb(0x08,0x7b,0xa7)
        self.img_start_record =  image.Image(int(self.disp_w * 0.3), int(self.disp_h * 0.2), bg=btn_color)
        size = image.string_size("START", 2)
        self.img_start_record.draw_string((self.img_start_record.width() - size.width())//2, (self.img_start_record.height() - size.height())//2, "START", image.COLOR_WHITE, 2)
        self.start_record_box = [0, self.disp_h - self.img_start_record.height(), self.img_start_record.width(), self.img_start_record.height()]
        
        self.img_stop_record =  image.Image(int(self.disp_w * 0.3), int(self.disp_h * 0.2), bg=btn_color)
        size = image.string_size("STOP", 2)
        self.img_stop_record.draw_string((self.img_stop_record.width() - size.width())//2, (self.img_stop_record.height() - size.height())//2, "STOP", image.COLOR_WHITE, 2)
        self.stop_record_box = [self.disp_w - self.img_stop_record.width(), self.disp_h - self.img_stop_record.height(), self.img_stop_record.width(), self.img_stop_record.height()]

        size = image.string_size("ZH", scale=2)
        self.language_box = [self.disp_w - size.width(), 0, size.width(), size.height()]

        self.status = AppStatus.IDLE

    def run_asr(self, pcm:bytes):
        self.asr_thread_exit = False
        self.asr_thread = threading.Thread(target=self.asr_thread_handle, args=[pcm], daemon=True)
        self.asr_thread.start()

    def asr_thread_handle(self, pcm:bytes):
        self.asr_thread_lock.acquire()
        frames = self.vad_duration_ms * self.recorder.sample_rate() // 1000 
        chunk_size = self.recorder.frame_size(frames)
        voice_start = False
        new_pcm = bytes()
        for i in range(0, len(pcm), chunk_size):
            chunk = pcm[i:i+chunk_size]
            if not voice_start:
                if self.vad.is_speech(chunk, self.recorder.sample_rate()):
                    print('found voice start')
                    voice_start = True
            else:
                new_pcm += chunk

        if self.need_save_pcm:
            self.save_pcm_to_wav('/root/speech_transcribe.wav', new_pcm)

        self.asr_result = self.asr.transcribe_raw(new_pcm)
        self.asr_thread_exit = True
        self.asr_thread_lock.release()

    def check_touch_box(self, t, box:list, oft:int = 0):
        """This method is used for exiting and you normally do not need to modify or call it.
            You usually don't need to modify it.
        """
        if t[2] and t[0] + oft > box[0] and t[0] < box[0] + box[2] + oft and t[1] + oft > box[1] and t[1] < box[1] + box[3] + oft:
            return True
        else:
            return False

    def save_pcm_to_wav(self, file:str, pcm:bytes):
        tmp_path = '/tmp/tmp.pcm'
        with open(tmp_path, 'wb') as f:
            f.write(pcm)
        os.system(f'echo y | ffmpeg -f s16le -ar 16000 -ac 1 -i {tmp_path} {file}')

    def draw_ui(self):
        img = image.Image(self.disp_w, self.disp_h, image.Format.FMT_RGB888, bg=image.COLOR_BLACK)
        if self.status == AppStatus.IDLE:
            if self.asr_result:
                img.draw_string(0, 50, self.asr_result, image.COLOR_WHITE)
            else:
                title_size = image.string_size(self.title, 1)
                img.draw_string((img.width()-title_size.width())//2, (img.height()-title_size.height())//2 - 50, self.title, image.COLOR_WHITE, 1)
        else:
            title_size = image.string_size(self.title, 1)
            img.draw_string((img.width()-title_size.width())//2, (img.height()-title_size.height())//2 - 50, self.title, image.COLOR_WHITE, 1)
        img.draw_image(self.exit_box[0], self.exit_box[1], self.img_exit)
        img.draw_image(self.start_record_box[0], self.start_record_box[1], self.img_start_record)
        img.draw_image(self.stop_record_box[0], self.stop_record_box[1], self.img_stop_record)
        if self.language == 'zh':
            img.draw_string(self.language_box[0], self.language_box[1], "ZH", image.COLOR_WHITE, scale=2)
        else:
            img.draw_string(self.language_box[0], self.language_box[1], "EN", image.COLOR_WHITE, scale=2)

        self.disp.show(img)

    def run(self):
        last_loop_ms = time.ticks_ms()
        while not app.need_exit():
            ts_data = self.ts.read()

            if self.status == AppStatus.IDLE:
                self.title = 'Click START to begin recording.'
                if self.check_touch_box(ts_data, self.start_record_box):
                    print('enter AppStatus.RECORDING')
                    self.status = AppStatus.RECORDING
            elif self.status == AppStatus.RECORDING:
                self.title = 'Click STOP to stop recording.'
                if self.check_touch_box(ts_data, self.stop_record_box):
                    print('enter AppStatus.TRANSCRIBE')
                    self.status = AppStatus.TRANSCRIBE

                print('recording..')
                if not self.recorder_pcm_buffer:
                    self.recorder_pcm_buffer = self.recorder.record(20)
                else:
                    self.recorder_pcm_buffer += self.recorder.record(20)
            elif self.status == AppStatus.TRANSCRIBE:
                self.title = 'Transcribing..'
                # print('start transcribe..')
                self.draw_ui()
                if self.recorder_pcm_buffer:
                    if self.need_save_pcm:
                        self.save_pcm_to_wav('/root/speech.wav', self.recorder_pcm_buffer)
                    self.run_asr(self.recorder_pcm_buffer)
                    self.recorder_pcm_buffer = None

                if self.asr_thread_exit:
                    self.status = AppStatus.IDLE
                    print('get asr result:', self.asr_result)
 
            if self.need_exit:
                app.set_exit_flag(True)
                break

            if self.check_touch_box(ts_data, self.exit_box, 20):
                self.need_exit = True

            if self.check_touch_box(ts_data, self.language_box, 20):
                self.asr_thread_lock.acquire()
                if self.language == 'zh':
                    self.language = 'en'
                    del self.asr
                    self.asr = nn.Whisper(model="/root/models/whisper-base/whisper-base.mud", language=self.language)
                else:
                    self.language = 'zh'
                    del self.asr
                    self.asr = nn.Whisper(model="/root/models/whisper-base/whisper-base.mud", language=self.language)
                self.asr_thread_lock.release()

            self.draw_ui()

            if time.ticks_ms() - last_loop_ms >= 10:
                last_loop_ms = time.ticks_ms()
            else:
                time.sleep_ms(10)

if __name__ == '__main__':
    a = App()
    a.run()
