from maix import audio, app, time

r = audio.Recorder("/root/test.wav", block=False)
r.volume(100)
r.reset(True)
print("channel:", r.channel())
print("sample rate:", r.sample_rate())

while not app.need_exit():
    remaining_frames = r.get_remaining_frames()
    need_frames = 50 * r.sample_rate() / 1000
    if remaining_frames > need_frames:
        data = r.record(50)
        print(f'record {len(data)} bytes')
    else:
        time.sleep_ms(50)
print("finish!")