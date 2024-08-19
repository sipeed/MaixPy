from maix import video, display, app

disp = display.Display()
d = video.Decoder('/root/output.mp4')
print(f'resolution: {d.width()}x{d.height()} bitrate: {d.bitrate()} fps: {d.fps()}')
d.seek(0)
while not app.need_exit():
    img = d.decode_video()
    if not img:
        d.seek(0)
        continue
    print(d.last_pts())
    disp.show(img)