'''
     SmolVLM VLM example.
     Supportted devices: MaixCAM2
     Not Supported devices: MaixCAM
     Models:
        - https://huggingface.co/sipeed/smolvlm-256m-instruct-maixcam2
'''
from maix import nn, err, log, sys, image, display

model = "/root/models/smolvlm-256m-instruct-maixcam2/model.mud"
log.set_log_level(log.LogLevel.LEVEL_ERROR, color = False)
disp = display.Display()

smolvlm = nn.SmolVLM(model)
in_w = smolvlm.input_width()
in_h = smolvlm.input_height()
in_fmt = smolvlm.input_format()
print(f"input size: {in_w}x{in_h}, format: {image.format_name(in_fmt)}")

def on_reply(obj, resp):
    print(resp.msg_new, end="")

smolvlm.set_system_prompt("Your a helpful assistant.")
smolvlm.set_reply_callback(on_reply)

# load and set image
img = image.load("/maixapp/share/picture/2024.1.1/ssd_car.jpg", format=in_fmt)
smolvlm.set_image(img, fit=image.Fit.FIT_CONTAIN) # if size not math, will auto resize first
disp.show(img)

msg = "Describe the picture"
print(">>", msg)
resp = smolvlm.send(msg)
err.check_raise(resp.err_code)


