from maix import nn

# Only MaixCAM2 supports this model.
whisper = nn.Whisper(model="/root/models/whisper-base/whisper-base.mud")

file_name = "/maixapp/share/audio/demo.wav"

res = whisper.transcribe(file_name)

print(res)
