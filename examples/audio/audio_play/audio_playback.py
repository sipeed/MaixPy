from maix import audio, time, app

p = audio.Player()
print("sample_rate:{} format:{} channel:{}".format(p.sample_rate(), p.format(), p.channel()))

with open('/root/output.pcm', 'rb') as f:
    ctx = f.read()

p.play(bytes(ctx))

while not app.need_exit():
    time.sleep_ms(10)

print("play finish!")