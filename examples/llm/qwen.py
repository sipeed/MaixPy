'''
     Qwen LLM example.
     Supportted devices: MaixCAM2
     Not Supported devices: MaixCAM
     Models:
        - https://huggingface.co/sipeed/Qwen2.5-1.5B-Instruct-maixcam2
        - https://huggingface.co/sipeed/Qwen2.5-0.5B-Instruct-maixcam2
'''
from maix import nn, err, log, sys

model = "/root/models/Qwen2.5-1.5B-Instruct/model.mud"
# model = "/root/models/Qwen2.5-0.5B-Instruct/model.mud"
log.set_log_level(log.LogLevel.LEVEL_ERROR, color = False)

def bytes_to_human(b):
    """Convert bytes to a human-readable format."""
    if b < 1024:
        return f"{b} B"
    elif b < 1024**2:
        return f"{b / 1024:.2f} KB"
    elif b < 1024**3:
        return f"{b / 1024**2:.2f} MB"
    else:
        return f"{b / 1024**3:.2f} GB"

def show_mem_info():
    print("memory info:")
    for k, v in sys.memory_info().items():
        print(f"\t{k:12}: {bytes_to_human(v)}")
    print("")

show_mem_info()
qwen = nn.Qwen(model)
show_mem_info()



def on_reply(obj, resp):
    print(resp.msg_new, end="")

qwen.set_system_prompt("You are Qwen, created by Alibaba Cloud. You are a helpful assistant.")
qwen.set_reply_callback(on_reply)

msg = "你好，请介绍你自己"
print(">>", msg)
resp = qwen.send(msg)
err.check_raise(resp.err_code)

msg = "请计算 1990 + 35的值，并给出计算过程"
print(">>", msg)
resp = qwen.send(msg)
err.check_raise(resp.err_code)

qwen.clear_context()

msg = "please calculate 1990 + 35"
print(">>", msg)
resp = qwen.send(msg)
err.check_raise(resp.err_code)
# print(resp.msg)

