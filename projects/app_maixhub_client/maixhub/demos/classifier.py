from maix import nn, image


class Demo:
    def __init__(self, model_path):
        self.model_path = model_path
        self.classifier = None

    def init(self):
        # camera.config(size=self.input_size)
        print("-- load model:", self.model_path)
        self.classifier = nn.Classifier(model=self.model_path, dual_buff = True)
        print("-- load ok")

    def input_size(self):
        return self.classifier.input_size()

    def loop(self, img, dis_img, key):
        res = self.classifier.classify(img)
        max_idx, max_prob = res[0]
        msg = "{:.2f}: {}".format(max_prob, self.classifier.labels[max_idx])
        h = image.string_size("A", scale = 2, thickness = 2)[1]
        dis_img.draw_string(2, 10, msg, scale = 2, color = image.COLOR_RED, thickness = -2)

    def __del__(self):
        if self.classifier:
            del self.classifier
