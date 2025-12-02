import requests, json, os
import librosa

class SensevoiceClient:
    def __init__(self, model = "", url="http://0.0.0.0:12347", lauguage="auto", stream=False):
        self.model = model
        self.url = url
        self.stream = stream
        self.launguage = lauguage
    def _check_service(self):
        try:
            response = requests.get(self.url + '/status')
            if response.status_code == 200:
                return True
        except:
            return False

    def _start_service(self):
        import time
        if not self._check_service():
            os.system("systemctl start sensevoice.service")

        while not self._check_service():
            print("Waiting for service to start...")
            time.sleep(1)

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
            response = requests.post(self.url + '/_stop_model')
            if response.status_code == 200:
                res = json.loads(response.text)
                return True if res["status"] == 'not loaded' else False
        except Exception as e:
            return False

    def start(self):
        if self._start_service():
            print("Service started successfully.")
        else:
            print("Failed to start service.")
            return False

        if self._start_model():
            print("Model started successfully.")
        else:
            print("Failed to start model.")
            return False
        return True

    def stop_model(self):
        self._stop_model()

    def stop(self):
        self._stop_model()
        self._stop_service()

    def get_wave_form(self, path):
        waveform, _ = librosa.load(path, sr=16000)
        return waveform

    def refer(self, filepath):
        if self.stream:
            print("Streaming mode, use refer_stream() instead.")
            return ""
        waveform = self.get_wave_form(filepath)
        data = {
            "audio_data": waveform.tolist(),
            "sample_rate": 16000,
            "launguage": "auto"
        }
        try:
            response = requests.post(self.url + '/asr', json=data)
            if response.status_code == 200:
                res = json.loads(response.text)
                return res.get("text", "")
            else:
                print(f"Requests failed: {response.status_code}")
                return ""
        except Exception as e:
            print("Requests failed:", e)
            return ""

    def refer_stream(self, filepath):
        if not self.stream:
            print("Streaming mode, use refer() instead.")
            return ""
        waveform = self.get_wave_form(filepath)
        data = {
            "audio_data": waveform.tolist(),
            "sample_rate": 16000,
            "launguage": "auto",
            "step": 0.1,
        }
        print('start post')
        try:
            response = requests.post(self.url + '/asr_stream', json=data, stream=True)
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    yield chunk.get("text", "")
        except Exception as e:
            print("Requests failed:", e)
            return ""

stream = True
client = SensevoiceClient(model="/root/models/sensevoice-maixcam2/model.mud", stream=stream)
if client.start() is False:
    print("Failed to start service or model.")
    exit()
if not stream:
    print('start refer')
    text = client.refer("example/zh.mp3")
    print(text)
else:
    print('start refer stream')
    for text in client.refer_stream("example/zh.mp3"):
        print(text)