from maix import nn, image, tensor
import os
import numpy as np

def parse_str_values(value : str) -> list[float]:
    if "," in value:
      final = []
      values = value.split(",")
      for v in values:
        final.append(float(v))
      return final
    else:
      return [float(value)]

def load_labels(model_path, path_or_labels : str):
    path = ""
    if not ("," in path_or_labels or " " in path_or_labels or "\n" in path_or_labels):
      path = os.path.join(os.path.dirname(model_path), path_or_labels)
    if path and os.path.exists(path):
      with open(path, encoding = "utf-8") as f:
        labels0 = f.readlines()
    else:
      labels0 = path_or_labels.split(",")
    labels = []
    for label in labels0:
        labels.append(label.strip())
    return labels

class My_Classifier:
    def __init__(self, model : str):
      self.model = nn.NN(model, dual_buff = False)
      self.extra_info = self.model.extra_info()
      self.mean = parse_str_values(self.extra_info["mean"])
      self.scale = parse_str_values(self.extra_info["scale"])
      self.labels = self.model.extra_info_labels()
      # self.labels = load_labels(model, self.extra_info["labels"]) # same as self.model.extra_info_labels()

    def classify(self, img : image.Image):
      outs = self.model.forward_image(img, self.mean, self.scale, copy_result = False)
      # 后处理， 以分类模型为例
      for k in outs.keys():
        out = nn.F.softmax(outs[k], replace=True)
        out = tensor.tensor_to_numpy_float32(out, copy = False).flatten()
        max_idx = out.argmax()
        return self.labels[max_idx], out[max_idx]

classifier = My_Classifier("/root/models/mobilenetv2.mud")
file_path = "/root/cat_224.jpg"
img = image.load(file_path, image.Format.FMT_RGB888)
if img is None:
    raise Exception(f"load image {file_path} failed")
label, score = classifier.classify(img)

print(label, score)

