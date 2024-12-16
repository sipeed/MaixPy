from maix import display, app, time, ext_dev

disp = display.Display()

mlx = ext_dev.mlx90640.MLX90640Celsius(
    5,
    ext_dev.mlx90640.FPS.FPS_32,
    ext_dev.cmap.Cmap.WHITE_HOT,
    5, 50, 0.95)

while not app.need_exit():
    img = mlx.image()
    disp.show(img)
    print("min: ", mlx.min_temp_point())
    print("max: ", mlx.max_temp_point())
    print("center: ", mlx.center_point())
    fps = time.fps()
    print(f"time: {1000/fps:.02f}ms, fps: {fps:.02f}")