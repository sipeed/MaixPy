from maix import audio, time, app

r = audio.Recorder()
r.volume(12)
print("sample_rate:{} format:{} channel:{}".format(r.sample_rate(), r.format(), r.channel()))

record_ms = 2000
start_ms = time.time_ms()
while not app.need_exit():
    data = r.record()
    print("data size", len(data))

    if time.time_ms() - start_ms > record_ms:
        app.set_exit_flag(True)

    time.sleep_ms(10)

print("record finish!")