from maix import nn, image, comm
import struct

class Demo:
    def __init__(self, model_path):
        self.model_path = model_path
        self.detector = None
        self.p = None
        self.APP_CMD_DETECT_RES = 0x02
        self.report_on = True

    def encode_objs(self, objs):
        '''
            encode objs info to bytes body for protocol
            2B x(LE) + 2B y(LE) + 2B w(LE) + 2B h(LE) + 2B idx + 4B score(float) ...
        '''
        body = b''
        for obj in objs:
            body += struct.pack("<hhHHHf", obj.x, obj.y, obj.w, obj.h, obj.class_id, obj.score)
        return body

    def init(self):
        self.detector = nn.YOLOv5(model=self.model_path, dual_buff = True)
        self.p = comm.CommProtocol(buff_size = 1024)

    def input_size(self):
        return self.detector.input_size()

    def loop(self, img, dis_img, key):
        objs = self.detector.detect(img, conf_th = 0.5, iou_th = 0.45)

        if len(objs) > 0 and self.report_on:
            body = self.encode_objs(objs)
            self.p.report(self.APP_CMD_DETECT_RES, body)

        for obj in objs:
            rect = image.resize_map_pos(img.width(), img.height(), dis_img.width(), dis_img.height(), image.Fit.FIT_CONTAIN, obj.x, obj.y, obj.w, obj.h)
            str_h = image.string_size(self.detector.labels[obj.class_id])[1]
            dis_img.draw_rect(rect[0], rect[1], rect[2], rect[3], color = image.COLOR_RED, thickness = 2)
            msg = f'{self.detector.labels[obj.class_id]}: {obj.score:.2f}'
            dis_img.draw_string(rect[0], rect[1] - str_h - 2, msg, color = image.COLOR_RED)


    def __del__(self):
        if self.detector:
            del self.detector
