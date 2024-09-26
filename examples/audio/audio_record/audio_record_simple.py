from maix import audio

r = audio.Recorder("/root/output.pcm")
r.volume(24)
print("sample_rate:{} format:{} channel:{}".format(r.sample_rate(), r.format(), r.channel()))

r.record(3000)
r.finish()

print("record finish!")