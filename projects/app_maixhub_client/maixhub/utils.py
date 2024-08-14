
from .trans import tr

def download_file(url, file_path, callback=lambda curr, total: False):
    try:
        import requests
        import os
        if os.path.exists(file_path):
            os.remove(file_path)
        r = requests.get(url, stream=True)
        if not r.status_code in [200, 206]:
            return False, tr("Refused")
        total = int(r.headers.get('content-length', 0))
        curr = 0
        cacel = False
        with open(file_path, 'wb') as f:
            i = 0
            for chunk in r.iter_content(chunk_size=4096):
                i += 1
                if chunk:
                    curr += len(chunk)
                    f.write(chunk)
                    f.flush()
                    cacel = callback(curr, total)
                    if cacel:
                        break
        if cacel:
            try:
                os.remove(file_path)
            except Exception:
                pass
            return False, tr("Canceled")
    except Exception as e:
        print("Download error:", e)
        return False, ""
    return True, ""

def unzip_files(zip_path, out_dir, check_subdir=True):
    '''
        @check_subdir: bool, if true, check subdir, e.g.
                    dataset.zip
                        dataset/
                                train/
                                val/
                    if set to True, will return out_dir is `out_dir/dataset` instead of `out_dir`
    '''
    try:
        import zipfile
        import os

        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(out_dir)
    except Exception as e:
        print(e)
        return False, "Unzip failed"
    if check_subdir:
        files = os.listdir(out_dir)
        files_valid = files.copy()
        for f in files:
            if f.startswith("."):
                files_valid.remove(f)
        sub_dir = os.path.join(out_dir, files_valid[0])
        if len(files_valid) == 1 and os.path.isdir(sub_dir):
            out_dir = sub_dir
    return True, ""

def remove_dir(path):
    try:
        import os
        if os.path.exists(path):
            names = os.listdir(path)
            for name in names:
                os.remove(os.path.join(path, name))
            os.rmdir(path)
    except Exception as e:
        print(f"delete dir {path} error:", e)

class Audio:
    def __init__(self, file_path):
        import wave, pyaudio
        self.pyaudio = pyaudio
        self.file_path = file_path
        wf = wave.open(self.file_path, 'rb')
        self.p = pyaudio.PyAudio()
        self.channels = wf.getnchannels()
        self.stream = self.p.open(
                        format=self.p.get_format_from_width(wf.getsampwidth()),
                        channels=self.channels,
                        rate=wf.getframerate(),
                        output=True,
                        start=False,
                        stream_callback=self._play)
        self._start = 0
        self._closed = False
        self.data = b''
        while 1:
            data = wf.readframes(1024)
            if not data:
                break
            self.data += data

    def __del__(self):
        self.close()

    def _play(self, in_data, frame_count, time_info, status):
        start = self._start
        self._start += frame_count * self.pyaudio.get_sample_size(self.pyaudio.paInt16) * self.channels
        data = self.data[start : self._start]
        if self._start >= len(self.data):
            self._start = 0
        return (data, self.pyaudio.paContinue)

    def play(self):
        self.stream.stop_stream()
        self.stream.start_stream()

    def close(self):
        try:
            if not self._closed:
                self.stream.stop_stream()
                self.stream.close()
                self.p.terminate()
                self._closed = True
        except Exception as e:
            import traceback
            traceback.print_exc()

def bytes_to_human(num : int):
    if num > 1024 * 1024 * 1024:
        return f"{num / 1024 / 1024 / 1024:.2f} GB"
    if num > 1024 * 1024:
        return f"{num / 1024 / 1024:.2f} MB"
    if num > 1024:
        return f"{num / 1024:.2f} KB"
    return  f"{num}B"
