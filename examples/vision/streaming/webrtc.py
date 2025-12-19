from maix import time, webrtc, camera, image

cam = camera.Camera(640, 480, image.Format.FMT_YVU420SP, fps=30)
server = webrtc.WebRTC()
server.bind_camera(cam)
server.start()

print(server.get_url())

while not app.need_exit():
    time.sleep(1)
