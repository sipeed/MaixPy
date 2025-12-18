from maix import sys
if sys.device_id().lower() != "maixcam2":
    raise ValueError("Only maixcam2 platform support this module")

import requests, json, os
import wave
import numpy as np
import threading
from maix import app, time

class Sensevoice:
    def __init__(self, model = "", url="http://0.0.0.0:12347", lauguage="auto", stream=False):
        self.model = model
        self.url = url
        self.stream = stream
        self.launguage = lauguage
        self.thread = None
        self.thread_is_exit = False
        self.thread_exit_code = 0
        self.heartbeat_thread = None

        self.last_ai_isp = int(app.get_sys_config_kv("npu", "ai_isp", "0"))
        if self.last_ai_isp:
            raise ValueError("Please turn off AI ISP first, try: app.set_sys_config_kv('npu', 'ai_isp', '0')")

        if not os.path.exists(model):
            raise ValueError(f'Model {self.model} is not existed!')

    def _check_service(self):
        try:
            response = requests.get(self.url + '/status')
            if response.status_code == 200:
                return True
        except:
            return False

    def _send_heartbeat(self):
        try:
            response = requests.get(self.url + '/heartbeat')
            if response.status_code == 200:
                return True
        except:
            return False

    def send_heartbeat_thread(self):
        while True:
            if not self._send_heartbeat():
                print('Send heartbeat failed!')
            time.sleep(10)

    def _start_service(self):
        if not self._check_service():
            os.system("systemctl start sensevoice.service")

        count = 0
        while not self._check_service():
            count += 1
            print(f"Waiting for service to start({count})...")
            time.sleep(1)

        if self.heartbeat_thread is None:
            self.heartbeat_thread = threading.Thread(target=self.send_heartbeat_thread, daemon=True)
            self.heartbeat_thread.start()
        return True

    def _stop_service(self):
        os.system("systemctl stop sensevoice.service")

    def _get_status(self):
        try:
            response = requests.get(self.url + '/status')
            if response.status_code == 200:
                res = json.loads(response.text)
                return res["status"]
        except:
            return "not loaded"

    def _reset_model(self):
        try:
            response = requests.post(self.url + '/reset_model')
            if response.status_code == 200:
                res = json.loads(response.text)
                return res["status"]
        except:
            return "not loaded"

    def _start_model(self):
        try:
            data = {
                "model_path": self.model,
                "sample_rate": 16000,
                "language": self.launguage,
                "stream": self.stream
            }
            response = requests.post(self.url + '/start_model', json=data)
            if response.status_code == 200:
                res = json.loads(response.text)
                return True if res["status"] == 'loaded' else False
        except Exception as e:
            return False

    def _stop_model(self):
        try:
            response = requests.post(self.url + '/stop_model')
            if response.status_code == 200:
                res = json.loads(response.text)
                return True if res["status"] == 'not loaded' else False
        except Exception as e:
            return False

    def _start_model_thread(self):
        print('Start service...')
        if self._start_service():
            print("Service started successfully.")
        else:
            print("Failed to start service.")
            self.thread_is_exit = True
            self.thread_exit_code = 1
            return False

        print('Start model...')
        if self._start_model():
            print("Model started successfully.")
        else:
            print("Failed to start model.")
            self.thread_is_exit = True
            self.thread_exit_code = 1
            return False

        self.thread_is_exit = True
        self.thread_exit_code = 0
        return True

    def start(self):
        self.thread_is_exit = False
        self.thread = threading.Thread(target=self._start_model_thread, daemon=True)
        self.thread.start()

    def is_ready(self, block=False):
        while not app.need_exit():
            if self.thread_is_exit:
                return True if self.thread_exit_code == 0 else False

            if self._get_status() == "loaded":
                return True
            else:
                if block:
                    time.sleep(1)
                else:
                    return False
        return False

    def stop(self):
        self._stop_model()
        self._stop_service()

    def load_wav_with_wave(self, path, sr=16000):
        """
        Load WAV file using wave library and resample to target sample rate
        """
        with wave.open(path, 'rb') as wav_file:
            # Get audio parameters
            n_channels = wav_file.getnchannels()
            sampwidth = wav_file.getsampwidth()
            framerate = wav_file.getframerate()
            n_frames = wav_file.getnframes()

            # Read audio data
            frames = wav_file.readframes(n_frames)

            # Convert byte data to numpy array based on sample width
            dtype_map = {1: np.int8, 2: np.int16, 4: np.int32}
            if sampwidth not in dtype_map:
                raise ValueError(f"Unsupported sample width: {sampwidth}")

            dtype = dtype_map[sampwidth]
            audio_data = np.frombuffer(frames, dtype=dtype)

            # Reshape for multi-channel audio
            if n_channels > 1:
                audio_data = audio_data.reshape(-1, n_channels)

            # Convert to float32 in range [-1, 1]
            audio_data = audio_data.astype(np.float32) / np.iinfo(dtype).max

            # Resample if needed
            if framerate != sr:
                # You'll need scipy for resampling
                from scipy import signal
                audio_data = signal.resample_poly(audio_data, sr, framerate, axis=0)

            return audio_data, sr

    def load_with_pcm(self, frames, sr=16000, bits=16, channels=1):
        if sr != 16000 or bits != 16 or channels != 1:
            raise ValueError("Only support samplerate = 16000, bits=16, channels=1")

        dtype = np.int16

        # Read audio data
        audio_data = np.frombuffer(frames, dtype=dtype)

        # Convert to float32 in range [-1, 1]
        audio_data = audio_data.astype(np.float32) / np.iinfo(dtype).max

        return audio_data, sr

    def get_wave_form(self, data:str | bytes):  # data is path or pcm data
        if isinstance(data, str):
            waveform, _ = self.load_wav_with_wave(data, sr=16000)
        elif isinstance(data, bytes):
            waveform, _ = self.load_with_pcm(data, sr=16000)
        else:
            raise ValueError("Not support this data type", type(data))
        return waveform

    def refer(self, path=None, audio_data=None):
        if self.stream:
            print("Streaming mode, use refer_stream() instead.")
            return ""

        if path:
            waveform = self.get_wave_form(path)
        elif audio_data:
            waveform = self.get_wave_form(audio_data)
        else:
            raise ValueError("You need input path or audio_data")

        data = {
            "audio_data": waveform.tolist(),
            "sample_rate": 16000,
            "launguage": "auto"
        }

        try:
            result = ""
            response = requests.post(self.url + '/asr', json=data)
            if response.status_code == 200:
                res = json.loads(response.text)
                text = res.get("text", "")
                if len(text) > 0:
                    result = text[0]
                else:
                    result = ""
            else:
                print(f"Requests failed: {response.status_code}")
                result = ""

            return result
        except Exception as e:
            print("Requests failed:", e)
            return ""

    def refer_stream(self, path=None, audio_data=None):
        if not self.stream:
            print("Streaming mode, use refer() instead.")
            return ""

        if path:
            waveform = self.get_wave_form(path)
        elif audio_data:
            waveform = self.get_wave_form(audio_data)
        else:
            raise ValueError("You need input path or audio_data")

        data = {
            "audio_data": waveform.tolist(),
            "sample_rate": 16000,
            "launguage": "auto",
            "step": 0.1,
        }

        try:
            response = requests.post(self.url + '/asr_stream', json=data, stream=True)
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    yield chunk.get("text", "")

            self._reset_model()
        except Exception as e:
            print("Requests failed:", e)
            return ""