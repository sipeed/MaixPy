'''
     Qwen3 VLM example.
     Supportted devices: MaixCAM2
     Not Supported devices: MaixCAM
     Models:
        - https://huggingface.co/sipeed/Qwen3-VL-2B-Instruct-GPTQ-Int4-AX630C-P320-CTX448-maixcam2
'''
from maix import app, nn, err, image, display, time
import requests
import json

model = "/root/models/Qwen3-VL-2B-Instruct-GPTQ-Int4-AX630C-P320-CTX448-maixcam2/model.mud"
disp = display.Display()

qwen3_vl = nn.Qwen3VL(model)

in_w = qwen3_vl.input_width()
in_h = qwen3_vl.input_height()
in_fmt = qwen3_vl.input_format()
print(f"input size: {in_w}x{in_h}, format: {image.format_name(in_fmt)}")

def on_reply(obj, resp):
    print(resp.msg_new, end="")

qwen3_vl.set_system_prompt("You are Qwen3VL. You are a helpful vision-to-text assistant.")
qwen3_vl.set_reply_callback(on_reply)

# load and set image
img = image.load("/maixapp/share/picture/2024.1.1/ssd_car.jpg", format=in_fmt)
qwen3_vl.set_image(img, fit=image.Fit.FIT_CONTAIN) # if size not math, will auto resize first
disp.show(img)

while not app.need_exit():
    print('wait model is ready')
    if qwen3_vl.is_ready():
        break
    time.sleep(1)

def example1():
    print('')
    # set prompt
    msg = "请描述图中有什么"
    print(">>", msg)
    resp = qwen3_vl.send(msg)
    err.check_raise(resp.err_code)

def example2():
    print('')
    msg = "Describe the picture"
    print(">>", msg)
    resp = qwen3_vl.send(msg)
    err.check_raise(resp.err_code)


def example3():
    print('')
    url = "http://127.0.0.1:12346"
    headers = {
        "Content-Type": "application/json",
    }

    stream = True
    data = {
        "model": "AXERA-TECH/Qwen3-VL-2B-Instruct-GPTQ-Int4",
        "stream":stream,
        "temperature":0.7,
        "repetition_penalty":1,
        "top-p":0.8,
        "top-k":20,
        "messages": [{
                "role":"user",
                "content": [{
                        "type":"text",
                        "text":"告诉我你的名字"
                    }, {
                        "type":"image_url",
                        "image_url":"images/demo.jpg"
                    }]
                }]
    }
    response = requests.post(url + '/v1/chat/completions', headers=headers, json=data, stream=stream)

    if not stream:
        print(response.status_code)  # 状态码
        print(response.text)         # 响应内容
    else:
        # 处理流式响应
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data_str = line[6:]  # 移除 "data: " 前缀
                        if data_str.strip() == '[DONE]':
                            print("\n流式传输完成")
                            break
                        try:
                            chunk = json.loads(data_str)
                            # 提取模型输出内容
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    print(delta['content'], end='', flush=True)
                        except json.JSONDecodeError:
                            continue
        else:
            print(f"请求失败: {response.status_code}")
            print(response.text)


example1()
# example2()
# example3()

del qwen3_vl        # Must release vlm object