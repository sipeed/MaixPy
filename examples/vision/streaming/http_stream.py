from maix import camera, time, app, http

html = """<!DOCTYPE html>
<html>
<head>
    <title>JPG Stream</title>
</head>
<body>
    <h1>MaixPy JPG Stream</h1>
    <img src="/stream" alt="Stream">
</body>
</html>"""

cam = camera.Camera(320, 240)
stream = http.JpegStreamer()
stream.set_html(html)
stream.start()

print("http://{}:{}".format(stream.host(), stream.port()))
while not app.need_exit():
    t = time.ticks_ms()
    img = cam.read()
    stream.write(img)
    print(f"time: {time.ticks_ms() - t}ms, fps: {1000 / (time.ticks_ms() - t)}")