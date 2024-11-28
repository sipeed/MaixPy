from maix import camera, time, app, rtmp, image, audio

AUDIO_ENABLE=True
audio_recorder = None
cam = camera.Camera(640, 480, image.Format.FMT_YVU420SP)

host="192.168.0.63"
port=1935
app_name="live"
stream_name="stream"
client = rtmp.Rtmp(host, port, app_name, stream_name)
client.bind_camera(cam)
if AUDIO_ENABLE:
    audio_recorder = audio.Recorder()
    client.bind_audio_recorder(audio_recorder)
client.start()

print(f"rtmp://{host}:{port}/{app_name}/{stream_name}")
while not app.need_exit():
    time.sleep(1)