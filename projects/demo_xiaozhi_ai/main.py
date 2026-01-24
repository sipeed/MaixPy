#!/usr/bin/env python
import os, importlib, subprocess, sys
import ssl      # Load the correct openssl
from maix import audio, image, app, display, time, fs, key

BG_COLOR = image.COLOR_WHITE
TEXT_COLOR = image.COLOR_BLACK

image.load_font("sourcehansans", "/maixapp/share/font/SourceHanSansCN-Regular.otf", 26)
image.set_default_font("sourcehansans")
logo = image.load('assets/xiaozhiai.png', image.Format.FMT_RGBA8888)
curr_emoji = 'neutral'
last_emoji = ''
already_draw_emoji = False
emoji_images = {}
emoji_images[curr_emoji] = image.load(f'assets/{curr_emoji}.png', image.Format.FMT_RGBA8888).resize(240, 240)
disp = display.Display()
img = image.Image(disp.width(), disp.height(), image.Format.FMT_RGBA8888)
img.draw_rect(0, 0, img.width(), img.height(), BG_COLOR, -1)
logo_x = (img.width() - logo.width()) // 2
logo_y = (img.height() - logo.height()) // 2
text_size = image.string_size('一二三四五六七八九十')
need_login = False

str_start_x = logo_x
str_start_y = logo_y + logo.height()

os.system("arecord -q -r 16000 -f S16_LE -c 1 -s 1024 /dev/null")

def get_board_name():
    with open('/proc/device-tree/model', 'r') as f:
        return f.read().lower().replace('\x00','')

def get_emoji_str(name: str) -> str:
    if name in emoji_images:
        return name
    else:
        return 'neutral'

def get_emoji_img(name: str):
    if name in emoji_images:
        return emoji_images[name]
    else:
        img_path = f'assets/{name}.png'
        if fs.exists(img_path):
            emoji_images[name] = image.load(img_path, image.Format.FMT_RGBA8888).resize(240, 240)
            return emoji_images[name]
        else:
            return emoji_images['neutral']

def draw_load_info(text, color = TEXT_COLOR):
    img.clear()
    img.draw_rect(0, 0, img.width(), img.height(), BG_COLOR, -1)
    img.draw_image(logo_x, logo_y, logo)
    str_size = image.string_size(text)
    img.draw_string((img.width() - str_size.width()) // 2, str_start_y, text, color)
    disp.show(img)

def draw_and_load_assets():
    draw_load_info('load image..')
    assets_path = 'assets'
    for filename in os.listdir(assets_path):
        if filename.lower().endswith('.png'):
            name = filename[:filename.find('.')]
            if name != 'xiaozhiai':
                get_emoji_img(name)

def load_module(module_name):
    draw_load_info(f"import {module_name}..")
    success = False
    module = None
    try:
        module = importlib.import_module(module_name)
        success = True
    except:
        if module_name == 'opuslib':
            draw_load_info(f"install {module_name}, may take a few minutes..")
            subprocess.check_call(['cp', 'deps/libopus.so', '/usr/lib'])
            subprocess.check_call([sys.executable, "-m", "pip", "install", '--force-reinstall', 'deps/opuslib-3.0.1.tar.gz'])
            subprocess.check_call(['sync'])
            try:
                module = importlib.import_module(module_name)
                success = True
            except ImportError:
                success = False
        else:
            success = False

    if not success:
        draw_load_info(f"import {module_name} failed, press boot to exit")
        while not app.need_exit():
            time.sleep_ms(100)
    return module

websockets = load_module('websockets')
uuid = load_module('uuid')
json = load_module('json')
struct = load_module('struct')
opuslib = load_module('opuslib')
np = load_module('numpy')
requests = load_module('requests')
asyncio = load_module('asyncio')
draw_and_load_assets()

def get_mac_address():
    mac=uuid.UUID(int = uuid.getnode()).hex[-12:].lower()
    return ":".join([mac[e:e+2] for e in range(0,11,2)])



DEVICE_ID = get_mac_address()
print('Mac Address: ', DEVICE_ID)

class Server:
    def __init__(self, **kwargs):
        self.mac = kwargs.get('mac', f'{DEVICE_ID}')
        self.state = 'idle'
        self.websocket = None
        self.wss_url = kwargs.get('wss_url', 'wss://api.tenclass.net/xiaozhi/v1/')
        self.https_url = kwargs.get('https_url', 'https://api.tenclass.net/xiaozhi/ota/')
        self.client_rate = kwargs.get('client_rate', 16000)
        self.client_channels = kwargs.get('clent_channels', 1)
        self.client_blockms = kwargs.get('client_blockms', 60)
        self.client_format = kwargs.get('client_format', 'int16')
        self.server_rate = 24000
        self.server_blockms = 60
        self.server_channels = 1
        self.server_format = 'int16'
        self.output_device = audio.Player(sample_rate=self.client_rate, block=True)
        if get_board_name() == 'maixcam2':
            self.output_device.volume(50)
        else:
            self.output_device.volume(100)
        self.output_device.period_size(960)
        # self.output_device.period_count(100)

        self.input_device = audio.Recorder(sample_rate=16000, block=False)
        self.input_device.volume(100)
        self.input_device.reset(True)
        time.sleep_ms(100)
        self.input_device.record(60)
        self.input_device.reset(False)
        self.input_device.period_size(1920)
        # self.input_device.period_count(100)
        self.play_queue = asyncio.Queue(100)

        self.opus_encoder = opuslib.Encoder(self.client_rate, self.client_channels, opuslib.APPLICATION_AUDIO)

        self.boot_key_count = 0
        self.boot_key = key.Key(self.on_key)

    def on_key(self, key_id, state):
        '''
            this func called in a single thread
        '''
        print(f"key: {key_id}, state: {state}") # key.c or key.State.KEY_RELEASED
        self.boot_key_count += 1

    def ready(self):
        self.display = disp
        image.load_font("sourcehansans", "/maixapp/share/font/SourceHanSansCN-Regular.otf", size = 24)
        image.set_default_font("sourcehansans")
        self.base_img = image.Image(self.display.width(), self.display.height(), image.Format.FMT_RGBA8888)
        self.base_img.draw_rect(0, 0, self.base_img.width(), self.base_img.height(), BG_COLOR, -1)
        str_say_something = '来说点什么吧~'
        font_size = image.string_size(str_say_something)

        self.base_img.draw_string(0, font_size.height() * 0, '来说点什么吧~', TEXT_COLOR)
        self.base_img.draw_string(0, font_size.height() * 1, 'Say something~', TEXT_COLOR)

        tips_en = 'Check the docs first(maixhub.com/app/95)'
        tips_en_size = image.string_size(tips_en)
        self.base_img.draw_string((self.base_img.width() - tips_en_size.width()) // 2, self.base_img.height() - tips_en_size.height(), tips_en, TEXT_COLOR, 0.7)

        tips_zh = '使用前先看看这里的文档说明哦(maixhub.com/app/95)'
        tips_zh_size = image.string_size(tips_en)
        self.base_img.draw_string((self.base_img.width() - tips_zh_size.width()) // 2, self.base_img.height() - tips_en_size.height() - tips_zh_size.height(), tips_zh, TEXT_COLOR, 0.7)
        
        self.display.show(self.base_img)

    async def set_state(self, state: str):
        '''
        state: "idle" | "wake_word_detected" | "listening" | "speaking"
        '''
        self.state = state
        await self.websocket.send(json.dumps({
            "type": "state",
            "state": state
        }))

    async def connect(self):
        draw_load_info('connect server..')
        while not app.need_exit():
            ok = False
            try:
                headers = {
                    "Authorization": "Bearer test-token",
                    "Protocol-Version": "3",
                    "Device-Id": f"{self.mac}",
                }
                if get_board_name() == 'maixcam2':
                    self.websocket = await websockets.connect(self.wss_url, additional_headers=headers)
                else:
                    self.websocket = await websockets.connect(self.wss_url, extra_headers=headers)
                ok = True
            except websockets.exceptions.InvalidURI as e:
                print(f"Invalid URI: {e}")
                exit(1)
            except Exception as e:
                print(f"An unexpected error occurred: {e}, {type(e)}")
                time.sleep_ms(100)
                ok = False
            if ok:
                break

    async def say_hello(self):
            message = {
                "type": "hello",
                "transport": "websocket",
                "version": 3,
                "response_mode": "realtime",
                "audio_params": {
                    "format": "opus",
                    "sample_rate": self.client_rate,
                    "channels": self.client_channels,
                    "frame_duration": self.client_blockms
                }
            }
            json_message = json.dumps(message)

            await self.websocket.send(json_message)
            print(f"Sent: {json_message}")

            response = await self.websocket.recv()
            response = json.loads(response)
            print(f"Received: {response}")

    async def check_version(self):
        wss_url = 'https://api.tenclass.net/xiaozhi/ota/'

        headers = {
            "Device-Id": f"{self.mac}",
            "Content-Type": "application/json",
        }

        data = {
            "flash_size": "4194304",
            "minimum_free_heap_size": "102400",
            "mac_address": f"{self.mac}",
            "chip_model_name": "esp32s3",
            "chip_info": {
                "model": "1",
                "cores": "2",
                "revision": "0",
                "features": "0",
            },
            "application": {
                "name": "my-app",
                "version": "1.0.0",
                "compile_time": "2021-01-01T00:00:00Z",
                "idf_version": "4.2-dev",
                "elf_sha256": "",
            },
            "partition_table": [
                {
                    "label": "app",
                    "type": 1,
                    "subtype": 2,
                    "address": 0x10000,
                    "size": 0x100000,
                },
            ],
            "ota": {
                "label": "ota_0",
            },
            "board": {
                "type": "",
                "revision": "",
                "carrier": "",
                "csq": "",
                "imei": "",
                "iccid": ""
            }
        }

        try:
            response = requests.post(wss_url, json=data, headers=headers)

            print("Status Code:", response.status_code)
            print("Response Headers:")
            for key, value in response.headers.items():
                print(f"{key}: {value}")

            print("Response Body (Text):", response.text)

            try:
                json_response = response.json()
                print("Response Body (JSON):", json_response)
            except ValueError:
                print("Response is not in JSON format.")

        except requests.exceptions.RequestException as e:
            print("Request failed:", e)

    def parse_binary_protocol(self, data):
        header_format = "!BBH"
        header_size = struct.calcsize(header_format)

        if len(data) < header_size:
            raise ValueError("Data is too short to contain a valid header")

        type_, reserved, payload_size = struct.unpack_from(header_format, data)

        if len(data) < header_size + payload_size:
            raise ValueError("Data is too short to contain the full payload")

        payload = data[header_size:header_size + payload_size]
        return (type_, payload_size, payload)

    def encode_binary_protocol(self, pcm_data):
        type_ = 0
        reserved = 0
        # print(f'type:{type(pcm_data)} length:{len(pcm_data)} channel:{self.client_channels}')
        payload = self.opus_encoder.encode(pcm_data, len(pcm_data) // self.client_channels // 2)
        payload_size = len(payload)

        header = struct.pack('!BBH', type_, reserved, payload_size)

        binary_data = header + payload

        return binary_data

    def downsample(self, input_data: bytes, original_rate, target_rate):
        input_data_np = np.frombuffer(input_data, dtype=np.int16)

        ratio = target_rate / original_rate
        new_length = int(len(input_data_np) * ratio)
        output_data = np.zeros(new_length, dtype=np.int16)

        for i in range(new_length):
            original_index = int(i / ratio)
            output_data[i] = input_data_np[original_index]

        return output_data.tobytes()

    async def websocket_recv_handler(self):
        decoder = opuslib.Decoder(fs=self.server_rate, channels=self.server_channels)
        while not app.need_exit():
            try:
                message = await asyncio.wait_for(
                    self.websocket.recv(),
                    timeout=1
                )
                if isinstance(message, str):
                    global curr_emoji
                    global last_emoji
                    global already_draw_emoji
                    message = json.loads(message)
                    print('recv json message', message)
                    need_draw_emotion = False
                    new_emotion_str = ''
                    if not already_draw_emoji:
                        need_draw_emotion = True
                        new_emotion_str = ''
                    elif 'emotion' in message:
                        new_emotion_str = get_emoji_str(message['emotion'])
                        need_draw_emotion = True

                    if need_draw_emotion:
                        curr_emoji = get_emoji_str(new_emotion_str)
                        if curr_emoji != last_emoji:
                            last_emoji = curr_emoji
                            curr_emoji_img = get_emoji_img(curr_emoji)
                            x = 0
                            y = self.base_img.height() - curr_emoji_img.height()
                            w = curr_emoji_img.width()
                            h = curr_emoji_img.height()
                            self.base_img.draw_rect(x, y, w, h, BG_COLOR, -1)
                            self.base_img.draw_image(x, y, curr_emoji_img)
                            self.display.show(self.base_img)
                            already_draw_emoji = True

                    if 'state' in message:
                        if message['state'] == 'sentence_start':
                            total_frames = self.output_device.period_count() * self.output_device.period_size()
                            print('play total frame', total_frames, 'remaining frame', self.output_device.get_remaining_frames())
                            while not app.need_exit():
                                remaining_frames = self.output_device.get_remaining_frames()
                                if remaining_frames >= total_frames:
                                    break
                                elif remaining_frames >= total_frames - 1024:
                                    await asyncio.sleep(0.07)
                                    break

                            # self.output_device.reset(False)
                            t = time.ticks_ms()
                            curr_emoji_img = get_emoji_img(curr_emoji)
                            x = curr_emoji_img.width()
                            y = self.base_img.height() - curr_emoji_img.height() + (curr_emoji_img.height() - text_size.height()) // 5
                            w = self.base_img.width() - curr_emoji_img.width()
                            h = self.base_img.height() - y
                            self.base_img.draw_rect(x, y, w, h, BG_COLOR, -1)
                            # self.base_img.draw_image(x, y, curr_emoji_img)
                            text = f'   {message["text"]}'
                            self.base_img.draw_string(x, y, text, TEXT_COLOR)

                            self.display.show(self.base_img)
                            print(f'disp show used {time.ticks_ms() - t}')
                            print('start recv pcm data')
                        elif message['state'] == 'stop':
                            total_frames = self.output_device.period_count() * self.output_device.period_size()
                            print('play total frame', total_frames, 'remaining frame', self.output_device.get_remaining_frames())
                            while not app.need_exit():
                                remaining_frames = self.output_device.get_remaining_frames()
                                if remaining_frames >= total_frames:
                                    break
                                elif remaining_frames >= total_frames - 1024:
                                    await asyncio.sleep(0.07)
                                    break
                            print('stop remain:', self.output_device.get_remaining_frames(), 'total:', total_frames)
                            # self.output_device.reset(False)
                            print('stop playback pcm data')
                            print('start listening')
                            await self.set_state('listening')
                            self.input_device.reset(True)
                        elif message['state'] == 'sentence_end':
                            if 'text' in message:
                                if '请登录到控制面板添加设备' in message['text']:
                                    global need_login
                                    need_login = True
                    elif message['type'] == 'stt':
                        x = 0
                        y = 0
                        w = self.base_img.width()
                        h = 100
                        self.base_img.draw_rect(x, y, w, h, BG_COLOR, -1)
                        text = f'{message["text"]}'
                        self.base_img.draw_string(x, y, text, TEXT_COLOR)
                        self.display.show(self.base_img)

                elif isinstance(message, bytes):
                    type_, payload_size, payload = self.parse_binary_protocol(message)

                    pcm = decoder.decode(payload, 2880)
                    resample_pcm = self.downsample(pcm, 24000, 16000)
                    print(f'play remaining frames: {self.output_device.get_remaining_frames()}, need frames:{len(resample_pcm) // self.output_device.frame_size()}')
                    self.output_device.play(resample_pcm)
                    # await self.play_queue.put(resample_pcm)
                else:
                    print("Unknown message type:", type(message))
            except asyncio.TimeoutError:
                continue
            except websockets.exceptions.ConnectionClosedError:
                print('message recv: connect closed')
                app.set_exit_flag(True)
            except Exception as e:
                print(f'{e}')
                app.set_exit_flag(True)
        del self.boot_key
        self.boot_key = None

async def main():
    server = Server()
    print('connect ..')
    await server.connect()

    print('say hello ..')
    await server.say_hello()

    print('register task ..')
    recv_task = asyncio.create_task(server.websocket_recv_handler())

    print('check version ..')
    await server.check_version()

    print('ready ..')
    server.ready()
    # print('set state to xxx ..')
    # await server.set_state('wake_word_detected')

    print('listening ..')
    await server.set_state('listening')
    server.input_device.reset(True)

    is_maixcam2 = get_board_name() == 'maixcam2'
    try:
        while not app.need_exit():
            if is_maixcam2:
                need_frames = 60 * server.input_device.sample_rate() / 1000
                data = server.input_device.record(60)
                if len(data):
                    new_data = server.encode_binary_protocol(data)
                    await server.websocket.send(new_data)
                else:
                    await asyncio.sleep(0.05)
            else:
                remaining_frames = server.input_device.get_remaining_frames()
                need_frames = 60 * server.input_device.sample_rate() / 1000
                if remaining_frames >= need_frames:
                    print(f'recv remaining frames: {remaining_frames}, need frames:{need_frames}')
                    data = server.input_device.record(60)
                    new_data = server.encode_binary_protocol(data)
                    await server.websocket.send(new_data)
                else:
                    await asyncio.sleep(0.01)
            if server.boot_key_count:
                print('try exit..')
                app.set_exit_flag(True)
                await server.websocket.close()
    except websockets.exceptions.ConnectionClosedError:
        print('audio recv: connect closed')
        app.set_exit_flag(True)
    except:
        app.set_exit_flag(True)

    tasks = [recv_task]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())

    if need_login:
        boot_key_count0 = 0
        def on_key(key_id, state):
            global boot_key_count0
            '''
                this func called in a single thread
            '''
            print(f"key: {key_id}, state: {state}") # key.c or key.State.KEY_RELEASED
            boot_key_count0 += 1
        boot_key = key.Key(on_key)
        app.set_exit_flag(False)
        while not app.need_exit() and boot_key_count0 == 0:
            time.sleep_ms(100)
