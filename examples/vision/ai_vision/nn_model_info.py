from maix import nn

model_path = "/root/models/yolov8n.mud"
# model_path = "/root/models/yolov8n.cvimodel"

model = nn.NN(model_path)
inputs = model.inputs_info()
outputs = model.outputs_info()

print("\ninputs:")
for layer in inputs:
    print(layer)

print("\noutputs:")
for layer in outputs:
    print(layer)

# if mud format, have extra info
print("\nextra info:")
for k, v in model.extra_info().items():
    print(f"\t[{k}]: {v}")


