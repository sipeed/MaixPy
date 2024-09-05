from maix import video, display, app, time

disp = display.Display()
d = video.Decoder('/root/output.mp4')
print(f'resolution: {d.width()}x{d.height()} bitrate: {d.bitrate()} fps: {d.fps()}')
d.seek(0)

last_us = time.ticks_us()
while not app.need_exit():
    ctx = d.decode_video()
    if not ctx:
        d.seek(0)
        continue

    img = ctx.image()

    while time.ticks_us() - last_us < ctx.duration_us():
        time.sleep_ms(1)
    last_us = time.ticks_us()

    disp.show(img)