from maix import nn, audio

# Only MaixCAM2 supports this model.
whisper = nn.Whisper(model="/root/models/whisper-base/whisper-base.mud")

use_default_file = True

if use_default_file:
    file_name = "/maixapp/share/audio/demo.wav"
    print('Use default file:', file_name)
    print('Start transcribing..')
    res = whisper.transcribe(file_name)
    print(res)
else:
    file_name = "/root/audio.wav"
    recorder = audio.Recorder(file_name, sample_rate=16000, channel=1)
    recorder.volume(80)
    print('Recording for 3 seconds..')
    recorder.record(3 * 1000)
    recorder.finish()

    print('Start transcribing..')
    res = whisper.transcribe(file_name)
    print(res)
