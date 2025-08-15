from maix import nn, audio

# Only MaixCAM2 supports this model.
sample_rate = 44100
p = audio.Player(sample_rate=sample_rate)
p.volume(80)

melotts = nn.MeloTTS(model="/root/models/melotts/melotts-zh.mud", speed = 0.8, language='zh')

pcm = melotts.infer('你好', output_pcm=True)
p.play(pcm)

