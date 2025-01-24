from maix import audio, app, time

p = audio.Player("/root/test.wav")
print("sample_rate:{} format:{} channel:{}".format(p.sample_rate(), p.format(), p.channel()))
p.volume(100)
p.play()

while not app.need_exit():
    total_frames = p.period_size() * p.period_count()
    idle_frames = p.get_remaining_frames()
    if  total_frames == idle_frames:
        break
    time.sleep_ms(100)

print("play finish!")