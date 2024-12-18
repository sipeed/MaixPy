from maix import nn, tensor, time
import numpy as np

model_path = "/root/models/yolov8n.mud"
run_times = 20

model = nn.NN(model_path, dual_buff=False)

# input
print("\ninputs:")
input_tensors = tensor.Tensors()
input_tensors_li = []
for layer in model.inputs_info():
    print(layer)
    data = np.zeros(layer.shape, dtype=np.float32)
    t = tensor.tensor_from_numpy_float32(data, copy = False)
    input_tensors.add_tensor(layer.name, t, False, False)
    # we use `copy = False` for add_tensor, so input_tensors' data is borrowed from t,
    # so we add to global var to prevent t to be collected until we don't use input_tensors anymore.
    input_tensors_li.append(t)

# forward
print("\nforward now")
count = 0
t = time.ticks_ms()
while count < run_times:
    outputs = model.forward(input_tensors, copy_result = False, dual_buff_wait=True)
    count += 1
t = (time.ticks_ms() - t) / run_times
print(f"forward complete, average forward time: {t} ms\n")

# forward dual buff mode
print("forward dual buff mode now")
count = 0
t = time.ticks_ms()
while count < run_times:
    outputs = model.forward(input_tensors, copy_result = False)
    count += 1
t = (time.ticks_ms() - t) / run_times
print(f"forward dual buff mode complete, average forward time: {t} ms\n")

# we not use `input_tensors` anymore, `input_tensors_li` can be deleted now
# del input_tensors_li

# output or add postprocess
for k in outputs.keys():
    out = tensor.tensor_to_numpy_float32(outputs[k], copy = False)
    print(f"out [{k}], shape: {out.shape}")


print("end")


