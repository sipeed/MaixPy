from maix import time, rtsp, camera, image

cam = camera.Camera(2560, 1440, image.Format.FMT_YVU420SP)
server = rtsp.Rtsp()
server.bind_camera(cam)
server.start()

print(server.get_url())

while True:
    time.sleep(1)