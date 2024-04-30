from maix import app, rtsp, camera, image, display

# init camera
cam = camera.Camera(2560, 1440, image.Format.FMT_YVU420SP)
cam2 = cam.add_channel(640, 480)

# init display
disp = display.Display()

# init rtsp server
server = rtsp.Rtsp()
server.bind_camera(cam)
server.start()

# draw region
rgn = server.add_region(0, 0, 200, 100)
canvas = rgn.get_canvas()
canvas.draw_string(0, 0, "Hello MaixPy")
rgn.update_canvas()

print(server.get_url())
while not app.need_exit():
    img = cam2.read()
    disp.show(img)

server.stop()