from maix import audio

r = audio.Recorder("/root/test.wav")
r.volume(100)
print("channel:", r.channel())
print("sample rate:", r.sample_rate())

print("record start!")
r.record(3000)
print("record finish!")