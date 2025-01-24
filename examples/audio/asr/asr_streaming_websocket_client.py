from maix import audio, app
import asyncio
import numpy as np
import websockets

SERVER_ADDR = "127.0.0.1"
SERVER_PORT = 6006

class AsrOnlineClient:
    def __init__(self, server_addr = "localhost", server_port = 6006):
        self.server_addr = server_addr
        self.server_port = server_port
        self.is_connected = False

        self.recorder = audio.Recorder(sample_rate=16000, channel=1, block=False)
        self.recorder.volume(100)
        self.recorder.reset(True)

        self.audio_queue = asyncio.Queue()
        pass  

    async def inputstream_generator(self):
        while not app.need_exit():
            indata, status = await self.audio_queue.get()
            yield indata, status
    async def receive_results(self, socket):
        last_message = ""
        async for message in socket:
            if message != "Done!":
                if last_message != message:
                    last_message = message

                    if last_message:
                        decode_message = last_message.encode().decode('unicode_escape')
                        print("Received: %s" % decode_message)
            else:
                return last_message

    async def run(self):
        async def record_audio():
            record_ms = 50
            bytes_per_frame = self.recorder.frame_size()
            record_bytes = record_ms * self.recorder.sample_rate() * bytes_per_frame  / 1000
            while not app.need_exit():
                while not app.need_exit():
                    remain_bytes = self.recorder.get_remaining_frames() * bytes_per_frame
                    if remain_bytes >= record_bytes:
                        data = self.recorder.record(50)
                        await self.audio_queue.put((data, 0))
                    else:
                        break
                await asyncio.sleep(0.005)

        server_url = f"ws://{self.server_addr}:{self.server_port}"
        try:
            async with websockets.connect(server_url) as websocket:  # noqa
                receive_task = asyncio.create_task(self.receive_results(websocket))
                print("Started! Please Speak")
                self.is_connected = True
                self.audio_task = asyncio.create_task(record_audio())
                
                async for indata, status in self.inputstream_generator():
                    if status:
                        print(status)
                    samples_int16 = np.frombuffer(indata, dtype=np.int16)
                    samples_float32 = samples_int16.astype(np.float32)
                    samples_float32 = samples_float32 / 32768
                    send_bytes = samples_float32.tobytes()
                    await websocket.send(send_bytes)

                decoding_results = await receive_task
                print(f"\nFinal result is:\n{decoding_results}")
        except Exception as e:
            print(f'Exception {e}')
        await self.audio_task
        pass 
async def main():
    try:
        client = AsrOnlineClient(SERVER_ADDR, SERVER_PORT)
    except ConnectionRefusedError:
        print('Check the server ip and port is correct!')
        return

    asr_task = asyncio.create_task(client.run())
    await asr_task

if __name__ == "__main__":
    asyncio.run(main())
