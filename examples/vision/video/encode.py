from maix import video, image, camera, app, time
import os

cam = camera.Camera(640, 480, image.Format.FMT_YVU420SP)
e = video.Encoder()
f = open('/root/output.h265', 'wb')

record_ms = 2000
start_ms = time.ticks_ms()
while not app.need_exit():
    img = cam.read()
    frame = e.encode(img)

    print(frame.size())
    f.write(frame.to_bytes(False))

    if time.ticks_ms() - start_ms > record_ms:
        app.set_exit_flag(True)
   
# Pack h265 to mp4
os.system('ffmpeg -loglevel quiet -i /root/output.h265 -c:v copy -c:a copy /root/output.mp4 -y')
