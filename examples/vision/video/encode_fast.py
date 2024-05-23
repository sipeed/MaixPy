from maix import video, time, image, camera, display, app
import os

cam = camera.Camera(640, 480, image.Format.FMT_YVU420SP)
disp = display.Display()
e = video.Encoder(capture = True)
e.bind_camera(cam)

f = open('/root/output.h265', 'wb')

record_ms = 2000
start_ms = time.time_ms()
while not app.need_exit():
    frame = e.encode()
    img = e.capture()
    disp.show(img)

    print(frame.size())
    f.write(frame.to_bytes(True))

    if time.time_ms() - start_ms > record_ms:
        app.set_exit_flag(True)

# Pack h265 to mp4
os.system('ffmpeg -loglevel quiet -i /root/output.h265 -c:v copy -c:a copy /root/output.mp4 -y')
