from maix import nn, image

class Demo:
    def __init__(self, model_path):
        self.model_path = model_path
        self.detector = None

    def init(self):
        self.detector = nn.YOLOv5(model=self.model_path, dual_buff = True)

    def input_size(self):
        return self.detector.input_size()

    def loop(self, img, dis_img, key):
        objs = self.detector.detect(img, conf_th = 0.5, iou_th = 0.45)
        for obj in objs:
            rect = image.resize_map_pos(img.width(), img.height(), dis_img.width(), dis_img.height(), image.Fit.FIT_CONTAIN, obj.x, obj.y, obj.w, obj.h)
            str_h = image.string_size(self.detector.labels[obj.class_id])[1]
            dis_img.draw_rect(rect[0], rect[1], rect[2], rect[3], color = image.COLOR_RED, thickness = 2)
            msg = f'{self.detector.labels[obj.class_id]}: {obj.score:.2f}'
            dis_img.draw_string(rect[0], rect[1] - str_h - 2, msg, color = image.COLOR_RED)


    def __del__(self):
        if self.detector:
            del self.detector
