from maix import camera, display, image, nn, app,time

detector = nn.YOLO26(model="/root/yolo26n.mud", dual_buff=False)
cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
disp = display.Display()

while not app.need_exit():
    img = cam.read()

    time.fps_start()
    objs = detector.detect(img, conf_th=0.5, iou_th=0.45)
    fps = time.fps()  
    print(f"time: {1000/fps:.02f}ms, fps: {fps:.02f}")

    for obj in objs:
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color=image.COLOR_RED)
        msg = f'{detector.labels[obj.class_id]}: {obj.score:.2f}'
        img.draw_string(obj.x, obj.y, msg, color=image.COLOR_RED)
    
    disp.show(img)