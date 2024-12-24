from maix import camera, display, app, image, audio
import asyncio, json, websockets
import numpy as np

STATUS_OK = 0
STATUS_EXIT = 1

class AsrOnlineClient:
    def __init__(self, exit_event):
        self.recorder = audio.Recorder(sample_rate=16000, channel=1)
        self.recorder.volume(100)
        self.audio_queue = asyncio.Queue()
        self.result_queue = asyncio.Queue()
        self.exit_event = exit_event
        pass  

    async def read_audio_queue(self):
        while not app.need_exit():
            indata, status = await self.audio_queue.get()
            yield indata, status

    async def read_asr_result(self):
        while not app.need_exit():
            res, status = await self.result_queue.get()
            yield res, status

    async def receive_results(self, socket):
        last_message = ""
        async for message in socket:
            if message != "Done!":
                if last_message != message:
                    last_message = message

                    if last_message:
                        decode_message = last_message.encode().decode('unicode_escape')
                        status = STATUS_OK if not app.need_exit() else STATUS_EXIT
                        await self.result_queue.put((json.loads(decode_message), status))
                        print("Received: %s" % decode_message)
            else:
                return last_message

    async def record_audio(self):
        while True:
            data = self.recorder.record(50)
            status = STATUS_OK if not app.need_exit() else STATUS_EXIT
            await self.audio_queue.put((data, status))
            await asyncio.sleep(0.005)

    async def run(self, queues):
        while not app.need_exit():
            ip, port = await queues[0].get()
            print(f'recv ip:{ip} port:{port}')
            server_url = f"ws://{ip}:{port}"
            try:
                async with websockets.connect(server_url) as websocket:
                    await queues[1].put('OK')
                    self.receive_task = asyncio.create_task(self.receive_results(websocket))
                    self.audio_task = asyncio.create_task(self.record_audio())
                    print("Started! Please Speak")
                    async for indata, status in self.read_audio_queue():
                        if status == STATUS_EXIT:
                            return
                        samples_int16 = np.frombuffer(indata, dtype=np.int16)
                        samples_float32 = samples_int16.astype(np.float32)
                        samples_float32 = samples_float32 / 32768
                        send_bytes = samples_float32.tobytes()
                        await websocket.send(send_bytes)
            except websockets.exceptions.ConnectionClosedError as e:
                await queues[1].put('SCAN AGAIN')
                print(f'websockets exception {e}')
            except websockets.exceptions.WebSocketException as e:
                await queues[1].put('SCAN AGAIN')
                print(f'websockets exception {e}')
            except Exception as e:
                await queues[1].put('SCAN AGAIN')
                print(f'exception {e}')

async def ui(cam, disp, client, queues):
    detector = image.QRCodeDetector()
    status = 1  # 0, standby 1,scan qrcode 2,show the result of asr
    err_msg = ''
    ip = ''
    port = 0
    while not app.need_exit():
        if status == 0:
            msg = await queues[1].get()
            if msg == 'OK':
                status = 2
            elif msg == 'SCAN AGAIN':
                status = 1
                err_msg = f'connect ws://{ip}:{port} failed!'
        elif status == 1:
            img = cam.read()
            qrcodes = detector.detect(img)
            if len(qrcodes) > 0:
                payload = qrcodes[0].payload()
                try:
                    json_res = json.loads(payload)
                    ip = json_res["ip"]
                    port = int(json_res["port"])
                    print(f'send ip:{ip} port:{port}')
                    img.clear()
                    img.draw_string(10, 10, f"connect to ws://{ip}:{port}..")
                    disp.show(img)
                    await queues[0].put((ip, port))
                    status = 0
                    continue
                except Exception as e:
                    print(f'Parse {payload} falied, except:{e}')
                    continue
            title = "Scan QRCode"
            msg1='1. Prepare a json string generated QR code.'
            msg2='the format of json: {"ip":"127.0.0.1","port":6006}'
            msg3='2. Put the qrcode in the screen.'
            img.draw_string(10, 10, title)
            img.draw_string(10, 40, msg1)
            img.draw_string(10, 70, msg2)
            img.draw_string(10, 100, msg3)
            img.draw_string(10, 130, err_msg, image.COLOR_RED)
            disp.show(img)
        else:
            base_img = image.Image(480, 320)
            base_img.draw_string(10, 10, "Please Speak..(Press the uesr key to exit)", font="sourcehansans")
            disp.show(base_img)
            try:
                async for res, status in client.read_asr_result():
                    if status == STATUS_EXIT:
                        return
                    print(f'res:{res}')
                    img = base_img.copy()
                    img.draw_string(10, 60, res['text'], image.COLOR_WHITE, font="sourcehansans")
                    disp.show(img)
            except:
                print('something exit')
                return


async def main():
    image.load_font("sourcehansans", "/maixapp/share/font/SourceHanSansCN-Regular.otf")
    cam = camera.Camera(480, 320)
    disp = display.Display()
    qrcode_queues = [asyncio.Queue(), asyncio.Queue()]
    exit_event = asyncio.Event()
    client = AsrOnlineClient(exit_event)
    
    ui_task = asyncio.create_task(ui(cam, disp, client, qrcode_queues))
    client_task = asyncio.create_task(client.run(qrcode_queues))
    tasks = [ui_task, client_task]
    try:
        await asyncio.gather(*tasks)
    except Exception as e:
        print(f'Exception caught: {e}')

if __name__ == '__main__':
    asyncio.run(main())