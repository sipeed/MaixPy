'''
    YOLO-World detection demo, if you want to detect different classes, please use nn_yolo_world_learn.py to generate feature file.
'''
from maix import camera, display, image, nn, app, touchscreen, time, audio
import os
import gc


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

class ASR:
    def __init__(self):
        self.whisper = nn.Whisper(model="/root/models/whisper-base/whisper-base.mud", language="en")
        self.recorder = audio.Recorder(sample_rate=16000, channel=1)
        self.recorder.volume(60)


    def record_mic(self, time_ms):
        print(f'Recording for {time_ms // 1000} seconds..')
        return self.recorder.record(time_ms)

    def transcribe_pcm(self, pcm):
        print('Start transcribing..')
        res = self.whisper.transcribe_raw(pcm)
        print('Transcription result:', res)
        return res.strip().replace(",", " ")

class APP:
    def __init__(self, disp):
        model = "/root/models/yolo-world_1_class.mud"
        feature = "/root/models/yolo-world_1_class_person.bin"
        labels = "/root/models/yolo-world_1_class_person.txt"
        self.model_valid = os.path.exists(model) and os.path.exists(feature) and os.path.exists(labels)
        self.disp = disp
        self.ts = touchscreen.TouchScreen()
        if self.model_valid:
            self._init_model(model, feature, labels)
        else:
            self.cam = camera.Camera(self.disp.width(), self.disp.height())
            self._update_button_info(self.cam.width(), self.cam.height())
        self.asr = ASR()
        image.load_font("sourcehansans", "/maixapp/share/font/SourceHanSansCN-Regular.otf", size = 24)
        # image.set_default_font("sourcehansans")

    def _init_model(self, model, feature, labels):
        self._destroy_model()
        self.detector = nn.YOLOWorld(model, feature, labels, dual_buff=True)
        self.cam = camera.Camera(self.detector.input_width(), self.detector.input_height(), self.detector.input_format())
        self._update_button_info(self.cam.width(), self.cam.height())
        self.model_valid = True

    def _update_button_info(self, img_w, img_h):
        self.img_back = get_back_btn_img(img_w)
        self.back_rect = [0, 0, self.img_back.width(), self.img_back.height()]
        self.back_rect_disp = image.resize_map_pos(img_w, img_h, self.disp.width(), self.disp.height(), image.Fit.FIT_CONTAIN,
                        self.back_rect[0], self.back_rect[1], self.back_rect[2], self.back_rect[3])
        self.btn_padding = 20 if img_w >= 640 else 10
        self.btn_learn_label = "Learn"
        self.btn_text_scale = 1.8 if img_w >= 640 else 1.4
        size = image.string_size(self.btn_learn_label, scale=self.btn_text_scale)
        self.learn_rect = [0, img_h - size.height() - int(self.btn_padding * 2), size.width() + int(self.btn_padding * 2), size.height() + int(self.btn_padding * 2)]
        self.learn_rect_disp = image.resize_map_pos(img_w, img_h, self.disp.width(), self.disp.height(), image.Fit.FIT_CONTAIN,
                        self.learn_rect[0], self.learn_rect[1], self.learn_rect[2], self.learn_rect[3])
        self.btn_yes_label = "Yes"
        self.btn_no_label = "No"
        size = image.string_size(self.btn_yes_label, scale=self.btn_text_scale)
        self.yes_rect = [0, img_h - size.height() - int(self.btn_padding * 2), size.width() + int(self.btn_padding * 2), size.height() + int(self.btn_padding * 2)]
        self.yes_rect_disp = image.resize_map_pos(img_w, img_h, self.disp.width(), self.disp.height(), image.Fit.FIT_CONTAIN,
                        self.yes_rect[0], self.yes_rect[1], self.yes_rect[2], self.yes_rect[3])
        size = image.string_size(self.btn_no_label, scale=self.btn_text_scale)
        self.no_rect = [img_w - size.width() - int(self.btn_padding * 2), img_h - size.height() - int(self.btn_padding * 2), size.width() + int(self.btn_padding * 2), size.height() + int(self.btn_padding * 2)]
        self.no_rect_disp = image.resize_map_pos(img_w, img_h, self.disp.width(), self.disp.height(), image.Fit.FIT_CONTAIN,
                        self.no_rect[0], self.no_rect[1], self.no_rect[2], self.no_rect[3])

    def _destroy_model(self):
        if hasattr(self, 'detector'):
            del self.detector
        if hasattr(self, 'cam'):
            del self.cam
        gc.collect()

    def _learn_obj(self, labels):

        out_dir = "/root/models/my_yolo_world"
        name = f"yolo-world_{'_'.join(labels)}".replace(" ", "_")
        os.makedirs(out_dir, exist_ok=True)
        if len(labels) == 0:
            raise ValueError("labels must not be empty")

        img = image.Image(self.disp.width(), self.disp.height(), bg=image.COLOR_BLACK)
        msg = f"Learning {", ".join(labels)} ..."
        msg_size = image.string_size(msg, scale=1.3)
        img.draw_string((img.width() - msg_size[0]) // 2, (img.height() - msg_size[1]) // 2, msg, scale=1.3, thickness=2, color=image.COLOR_WHITE)
        self.disp.show(img)

        feature_file = os.path.join(out_dir, f"{name}.bin")
        labels_file = os.path.join(out_dir, f"{name}.txt")
        with open(labels_file, "w") as f:
            for label in labels:
                f.write(f"{label}\n")

        cmd = f"python -u -m yolo_world_utils gen_text_feature --labels_path {labels_file} --out_feature_path {feature_file}"

        print(f"Now run\n\t`{cmd}`\nto generate text feature of\n{labels}")
        print("\nplease wait a moment, it may take a few seconds ...\n")
        ret = os.system(cmd)
        if ret != 0:
            print("[ERROR] execute have error, please see log")
            raise RuntimeError("Failed to generate text feature")
        else:
            print(f"saved\n\tlabels to:\n\t{labels_file}\n and text feature to:\n\t{feature_file}")
            print(f"please use yolo-world_{len(labels)}_class.mud model to run detect")
        model = f"/root/models/yolo-world_{len(labels)}_class.mud"
        self._init_model(model, feature_file, labels_file)



    def run(self):
        last_preesed = False
        ensure_label = False
        new_label = ""
        while not app.need_exit():
            img = self.cam.read()
            if self.model_valid:
                objs = self.detector.detect(img, conf_th=0.5, iou_th=0.45)
                for obj in objs:
                    img.draw_rect(obj.x, obj.y, obj.w, obj.h, color=image.COLOR_RED, thickness=3)
                    msg = f'{self.detector.labels[obj.class_id]}: {obj.score:.2f}'
                    img.draw_string(obj.x, obj.y, msg, color=image.COLOR_RED)
            else:
                msg = f"Push btn to learn object like 'person'"
                msg_size = image.string_size(msg, scale=self.btn_text_scale, thickness=2)
                img.draw_string((img.width() - msg_size[0]) // 2, (img.height() - msg_size[1]) // 2, msg, scale=self.btn_text_scale, thickness=5, color=image.COLOR_WHITE)
                img.draw_string((img.width() - msg_size[0]) // 2, (img.height() - msg_size[1]) // 2, msg, scale=self.btn_text_scale, thickness=2, color=image.COLOR_RED)
            img.draw_image(0, 0, self.img_back)
            img.draw_rect(self.learn_rect[0], self.learn_rect[1], self.learn_rect[2], self.learn_rect[3], image.COLOR_GRAY, thickness=-1)
            img.draw_rect(self.learn_rect[0], self.learn_rect[1], self.learn_rect[2], self.learn_rect[3], image.COLOR_WHITE, thickness=2)
            img.draw_string(self.learn_rect[0] + self.btn_padding, self.learn_rect[1] + self.btn_padding, self.btn_learn_label, image.COLOR_WHITE, scale=self.btn_text_scale)
            x, y, preesed = self.ts.read()
            if preesed:
                last_preesed = True
                print("pressed")
            elif last_preesed:
                print("click")
                last_preesed = False
                if is_in_button(x, y, self.back_rect_disp):
                    app.set_exit_flag(True)
                if ensure_label:
                    print("ensure_label ing")
                    if is_in_button(x, y, self.yes_rect_disp):
                        print("yes, now learn")
                        self._learn_obj([new_label])
                        ensure_label = False
                    elif is_in_button(x, y, self.no_rect_disp):
                        print("no, give up learn", new_label)
                        ensure_label = False
                else:
                    print("not ensure_label ing")
                    if is_in_button(x, y, self.learn_rect_disp):
                        print("listen new label")
                        msg = f"Say new label(English) in 3 seconds ..."
                        msg_size = image.string_size(msg, scale=self.btn_text_scale, thickness=2)
                        img = image.Image(img.width(), img.height(), bg = image.COLOR_BLACK)
                        img.draw_string((img.width() - msg_size[0]) // 2, (img.height() - msg_size[1]) // 2, msg, scale=self.btn_text_scale, thickness=5, color=image.COLOR_WHITE)
                        img.draw_string((img.width() - msg_size[0]) // 2, (img.height() - msg_size[1]) // 2, msg, scale=self.btn_text_scale, thickness=1, color=image.COLOR_RED)
                        self.disp.show(img)
                        pcm = self.asr.record_mic(3000)
                        msg = f"Transcribing ..."
                        msg_size = image.string_size(msg, scale=self.btn_text_scale, thickness=2)
                        img = image.Image(img.width(), img.height(), bg = image.COLOR_BLACK)
                        img.draw_string((img.width() - msg_size[0]) // 2, (img.height() - msg_size[1]) // 2, msg, scale=self.btn_text_scale, thickness=5, color=image.COLOR_WHITE)
                        img.draw_string((img.width() - msg_size[0]) // 2, (img.height() - msg_size[1]) // 2, msg, scale=self.btn_text_scale, thickness=1, color=image.COLOR_RED)
                        self.disp.show(img)
                        new_label = self.asr.transcribe_pcm(pcm)
                        if new_label:
                            ensure_label = True
                        # clear btn event
                        while self.ts.available():
                            x, y, last_preesed = self.ts.read()
            if ensure_label:
                msg = f"Ensure new label: {new_label} ?"
                msg2 = "Only support English!"
                msg_size = image.string_size(msg, scale=self.btn_text_scale, thickness=5, font="sourcehansans")
                msg_size2 = image.string_size(msg2, scale=self.btn_text_scale, thickness=2)
                img = image.Image(img.width(), img.height(), bg = image.COLOR_BLACK)
                img.draw_string((img.width() - msg_size[0]) // 2, (img.height() - msg_size2[1] - msg_size[1]) // 2, msg, scale=self.btn_text_scale, thickness=5, color=image.COLOR_WHITE, font="sourcehansans")
                img.draw_string((img.width() - msg_size[0]) // 2, (img.height() - msg_size2[1] - msg_size[1]) // 2, msg, scale=self.btn_text_scale, thickness=2, color=image.COLOR_RED, font="sourcehansans")
                img.draw_string((img.width() - msg_size2[0]) // 2, (img.height() - msg_size2[1] - msg_size[1]) // 2 + msg_size[1] + msg_size[1] // 2 , msg2, scale=self.btn_text_scale, thickness=2, color=image.COLOR_WHITE)
                img.draw_rect(self.yes_rect[0], self.yes_rect[1], self.yes_rect[2], self.yes_rect[3], image.COLOR_GRAY, thickness=-1)
                img.draw_rect(self.yes_rect[0], self.yes_rect[1], self.yes_rect[2], self.yes_rect[3], image.COLOR_WHITE, thickness=2)
                img.draw_string(self.yes_rect[0] + self.btn_padding, self.yes_rect[1] + self.btn_padding, self.btn_yes_label, image.COLOR_WHITE, scale=self.btn_text_scale)
                img.draw_rect(self.no_rect[0], self.no_rect[1], self.no_rect[2], self.no_rect[3], image.COLOR_GRAY, thickness=-1)
                img.draw_rect(self.no_rect[0], self.no_rect[1], self.no_rect[2], self.no_rect[3], image.COLOR_WHITE, thickness=2)
                img.draw_string(self.no_rect[0] + self.btn_padding, self.no_rect[1] + self.btn_padding, self.btn_no_label, image.COLOR_WHITE, scale=self.btn_text_scale)
            self.disp.show(img)


disp = display.Display()
try:
    app_instance = APP(disp)
    app_instance.run()
except Exception:
    import traceback
    msg = traceback.format_exc()
    print(msg)
    img = image.Image(disp.width(), disp.height(), bg=image.COLOR_BLACK)
    img.draw_string(0, 0, msg, image.COLOR_WHITE)
    disp.show(img)
    while not app.need_exit():
        time.sleep_ms(100)
