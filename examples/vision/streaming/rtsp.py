from maix import time, rtsp, camera, image, audio

AUDIO_ENABLE=True
audio_recorder = None
cam = camera.Camera(640, 480, image.Format.FMT_YVU420SP)
server = rtsp.Rtsp()
server.bind_camera(cam)
if AUDIO_ENABLE:
    audio_recorder = audio.Recorder()
    server.bind_audio_recorder(audio_recorder)
server.start()

print(server.get_url())

while True:
    time.sleep(1)