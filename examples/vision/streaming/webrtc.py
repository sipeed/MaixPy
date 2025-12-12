from maix import time, webrtc, camera, image

cam = camera.Camera(640, 480, image.Format.FMT_YVU420SP)
server = webrtc.WebRTC()
server.bind_camera(cam)
server.start()

print(server.get_url())

while True:
    time.sleep(1)
