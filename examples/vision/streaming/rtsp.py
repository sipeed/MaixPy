from maix import time, rtsp, camera, image

server = rtsp.Rtsp()
cam = camera.Camera(2560, 1440, image.Format.FMT_YVU420SP)
server.bind_camera(cam)
server.start()

print(server.get_url())

while True:
    time.sleep(1)