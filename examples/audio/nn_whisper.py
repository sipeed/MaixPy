from maix import nn

# Only MaixCAM Pro supports this model.
whisper = nn.Whisper(model="/root/models/whisper-base/whisper-base.mud")

file_name = "/maixapp/share/audio/demo.wav"

res = whisper.forward(file_name)

print(res)
