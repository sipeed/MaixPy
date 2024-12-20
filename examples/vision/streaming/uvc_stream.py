from maix import camera, display, app, time, uvc

cam = camera.Camera(640, 360, fps=60)   # Manually set resolution
                                # | 手动设置分辨率
# disp = display.Display()        # MaixCAM default is 522x368
                                # | MaixCAM 默认是 522x368

uvcs = uvc.UvcStreamer()
uvcs.use_mjpg(1)

while not app.need_exit():
    # time.fps_start()          # Manually set fps calculation start point, comment here mean last time fps() call is start
                                # | 动设置帧率（FPS）计算开始点，这里注释了表示上一次 fps 函数即是开始
    img = cam.read()            # Get one frame from camera, img is maix.image.Image type object
                                # | 从摄像头获取一帧图像，img 是 maix.image.Image 类型的对象
    # disp.show(img)              # Show image to screen
                                # | 将图像显示到屏幕
    uvcs.show(img)

    fps = time.fps()            # Calculate FPS between last time fps() call and this time call.
                                # | 计算两次 fps 函数调用之间的帧率
    print(f"time: {1000/fps:.02f}ms, fps: {fps:.02f}") # print FPS in console
                                                       # | 在终端打印帧率（FPS）

