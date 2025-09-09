from maix import audio

p = audio.Player("/root/test.wav")
print("sample_rate:{} format:{} channel:{}".format(p.sample_rate(), p.format(), p.channel()))
p.volume(80)
p.play()

print("play finish!")