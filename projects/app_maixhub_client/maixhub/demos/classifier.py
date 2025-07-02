from maix import nn, image, comm
import struct

class Demo:
    def __init__(self, model_path):
        self.model_path = model_path
        self.classifier = None
        self.p = None
        self.APP_CMD_CLASSIFY_RES = 0x02

    def encode_objs(self, res):
        '''
            encode objs info to bytes body for protocol
            2B max idx, 4B prob, 2B second idx, 4B prob, 2B third idx, 4B prob
        '''
        body = b''
        for obj in res:
            body += struct.pack("<Hf", obj[0], obj[1])
        return body

    def init(self):
        # camera.config(size=self.input_size)
        print("-- load model:", self.model_path)
        self.classifier = nn.Classifier(model=self.model_path, dual_buff = True)
        print("-- load ok")
        self.p = comm.CommProtocol(buff_size = 1024)

    def input_size(self):
        return self.classifier.input_size()

    def loop(self, img, dis_img, key):
        res = self.classifier.classify(img)

        body = self.encode_objs(res)
        self.p.report(self.APP_CMD_CLASSIFY_RES, body)

        max_idx, max_prob = res[0]
        msg = "{:.2f}: {}".format(max_prob, self.classifier.labels[max_idx])
        h = image.string_size("A", scale = 2, thickness = 2)[1]
        dis_img.draw_string(2, 10, msg, scale = 2, color = image.COLOR_RED, thickness = -2)

    def __del__(self):
        if self.classifier:
            del self.classifier
