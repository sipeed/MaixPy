from maix import audio, app, time
import threading
from queue import Queue, Empty

class StreamPlayer:
    def __init__(self, sample_rate=16000, channel=1, block:bool=False):
        self.p = audio.Player(sample_rate=sample_rate, channel=channel, block=block)
        self.p.volume(50)
        zero_data = bytes([0] * 4096)
        self.p.play(zero_data)
        self.queue = Queue(maxsize=250)
        self.t = threading.Thread(target=self.__thread, daemon=True)
        self.t.start()

    def wait_idle_size(self, size:int):
        while not app.need_exit():
            idle_frames = self.p.get_remaining_frames()
            write_frames = size / self.p.frame_size()
            if idle_frames >= write_frames:
                break
            time.sleep_ms(10)

    def __thread(self):
        while not app.need_exit():
            try:
                pcm = self.queue.get(timeout=500)
                # wait player is idle
                self.wait_idle_size(len(pcm))
                self.p.play(pcm)
            except Empty:
                continue

    def write(self, pcm:bytes):
        remain_len = len(pcm)
        period_bytes = self.p.frame_size() * self.p.period_size()
        offset = 0
        while remain_len > 0:
            write_bytes = period_bytes if period_bytes <= remain_len else period_bytes - remain_len
            new_pcm = pcm[offset:offset+write_bytes]
            self.queue.put(new_pcm)
            remain_len -= write_bytes
            offset += write_bytes

    def wait_finish(self):
        total_frames = self.p.period_count() * self.p.period_size()
        while not app.need_exit():
            idle_frames = self.p.get_remaining_frames()
            if idle_frames == total_frames:
                break
            time.sleep_ms(10)

if __name__ == '__main__':
    stream_player = StreamPlayer()
    with open('/maixapp/share/audio/demo.wav', 'rb') as f:
        pcm = f.read()
        t = time.ticks_ms()
        stream_player.write(pcm)
        print(f'write pcm data cost {time.ticks_ms() - t} ms')

        t = time.ticks_ms()
        stream_player.wait_finish()
        print(f'write play finish cost {time.ticks_ms() - t} ms')

