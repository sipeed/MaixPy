from maix import audio, time, app
print(000)
p = audio.Player()
print("sample_rate:{} format:{} channel:{}".format(p.sample_rate(), p.format(), p.channel()))

with open('/root/output.pcm', 'rb') as f:
    ctx = f.read()
print(111)
p.play(bytes(ctx))
print(222)
while not app.need_exit():
    time.sleep_ms(10)
print(333)
print("play finish!")