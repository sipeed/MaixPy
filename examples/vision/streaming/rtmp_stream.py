from maix import camera, time, app, rtmp, image

cam = camera.Camera(320, 240, image.Format.FMT_YVU420SP)

host="192.168.0.30"
port=1935
app_name="live"
stream_name="stream"
client = rtmp.Rtmp(host, port, app_name, stream_name)
client.bind_camera(cam)
client.start()

print(f"rtmp://{host}:{port}/{app_name}/{stream_name}")
while not app.need_exit():
    time.sleep(1)