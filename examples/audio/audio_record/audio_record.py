from maix import audio, time, app

r = audio.Recorder()
r.volume(12)
print("sample_rate:{} format:{} channel:{}".format(r.sample_rate(), r.format(), r.channel()))

while not app.need_exit():
    data = r.record()
    print("data size", len(data))

    time.sleep_ms(10)

print("record finish!")