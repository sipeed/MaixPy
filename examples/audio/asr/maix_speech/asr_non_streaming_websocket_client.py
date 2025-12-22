#!/usr/bin/env python3

from maix import audio
import asyncio
import json
import wave
import numpy as np
import websockets

SERVER_ADDR = "127.0.0.1"
SERVER_PORT = 6006
def read_wave(wave_filename: str) -> np.ndarray:
    with wave.open(wave_filename) as f:
        assert f.getframerate() == 16000, f.getframerate()
        assert f.getnchannels() == 1, f.getnchannels()
        assert f.getsampwidth() == 2, f.getsampwidth()  # it is in bytes
        num_samples = f.getnframes()
        samples = f.readframes(num_samples)
        samples_int16 = np.frombuffer(samples, dtype=np.int16)
        samples_float32 = samples_int16.astype(np.float32)

        samples_float32 = samples_float32 / 32768
        return samples_float32

async def receive_results(socket):
    last_message = ""
    async for message in socket:
        if message != "Done!":
            last_message = message
            print(json.loads(message))
        else:
            break
    return last_message


async def run(
    server_addr: str,
    server_port: int,
    wave_filename: str,
    samples_per_message: int,
    seconds_per_message: float,
):
    data = read_wave(wave_filename)

    async with websockets.connect(
        f"ws://{server_addr}:{server_port}"
    ) as websocket:  # noqa
        receive_task = asyncio.create_task(receive_results(websocket))

        start = 0
        while start < data.shape[0]:
            end = start + samples_per_message
            end = min(end, data.shape[0])
            d = data.data[start:end].tobytes()

            await websocket.send(d)
            await asyncio.sleep(seconds_per_message)
            start += samples_per_message

        await websocket.send("Done")
        await receive_task

async def main():
    wav_path = "/tmp/test.wav"
    recorder = audio.Recorder(wav_path, sample_rate=16000, channel=1)
    recorder.volume(100)
    print('Please Speak..')
    recorder.record(3 * 1000)
    recorder.finish()
    print('Recording complete, upload wav file to server..')

    await run(
        server_addr=SERVER_ADDR,
        server_port=SERVER_PORT,
        wave_filename=wav_path,
        samples_per_message=8000,
        seconds_per_message=0.1,
    )

if __name__ == "__main__":
    asyncio.run(main())
