'''
     InternVL VLM example.
     Supportted devices: MaixCAM2
     Not Supported devices: MaixCAM
     Models:
        - https://huggingface.co/sipeed/InternVL2.5-1B-maixcam2
'''
from maix import nn, err, log, sys, image, display

model = "/root/models/InternVL2.5-1B/model.mud"
log.set_log_level(log.LogLevel.LEVEL_ERROR, color = False)
disp = display.Display()

def show_mem_info():
    print("memory info:")
    for k, v in sys.memory_info().items():
        print(f"\t{k:12}: {sys.bytes_to_human(v)}")
    print("")

show_mem_info()
internvl = nn.InternVL(model)
show_mem_info()

in_w = internvl.input_width()
in_h = internvl.input_height()
in_fmt = internvl.input_format()
print(f"input size: {in_w}x{in_h}, format: {image.format_name(in_fmt)}")

def on_reply(obj, resp):
    print(resp.msg_new, end="")

internvl.set_system_prompt("你是由上海人工智能实验室联合商汤科技开发的书生多模态大模型，英文名叫InternVL, 是一个有用无害的人工智能助手。")
internvl.set_reply_callback(on_reply)

# load and set image
img = image.load("/maixapp/share/picture/2024.1.1/ssd_car.jpg", format=in_fmt)
internvl.set_image(img, fit=image.Fit.FIT_CONTAIN) # if size not math, will auto resize first
disp.show(img)

# set prompt
msg = "请描述图中有什么"
print(">>", msg)
resp = internvl.send(msg)
err.check_raise(resp.err_code)

msg = "Describe the picture"
print(">>", msg)
resp = internvl.send(msg)
err.check_raise(resp.err_code)
# print(resp.msg)


