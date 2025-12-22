from maix import sensevoice

open_microphone = False
stream = True
model_path = "/root/models/sensevoice-maixcam2"
client = sensevoice.Sensevoice(model=model_path+"/model.mud", stream=stream)
client.start()
if client.is_ready(block=True) is False:
    print("Failed to start service or model.")
    exit()

if open_microphone:
    from maix import audio
    recorder = audio.Recorder(sample_rate=16000, channel=1)
    recorder.volume(100)
    print('Recording for 3 seconds..')
    audio_data = recorder.record(3 * 1000)
    if not stream:
        print('start refer')
        text = client.refer(audio_data=audio_data)
        print(text)
    else:
        print('start refer stream')
        for text in client.refer_stream(audio_data=audio_data):
            print(text)
else:
    audio_file = "/maixapp/share/audio/demo.wav"
    if not stream:
        print('start refer')
        text = client.refer(path=audio_file)
        print(text)
    else:
        print('start refer stream')
        for text in client.refer_stream(path=audio_file):
            print(text)


# You can comment out this line of code, which will save time on the next startup. 
# But it will cause the background service to continuously occupy CMM memory.
client.stop()