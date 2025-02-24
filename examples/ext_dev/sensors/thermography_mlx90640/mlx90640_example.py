from maix import display, app, time, ext_dev
import os

disp = display.Display()

I2C_BUS_NUM = 5

if I2C_BUS_NUM == 5:
    ### 使用I2C5，尝试加载外设驱动。如果外设驱动已存在会有错误提示，忽略即可。
    ### Using I2C5, try to load the peripheral driver.
    ### If the peripheral driver already exists there will be an error message, just ignore it.
    os.system("insmod /mnt/system/ko/i2c-algo-bit.ko")
    os.system("insmod /mnt/system/ko/i2c-gpio.ko")


mlx = ext_dev.mlx90640.MLX90640Celsius(
    I2C_BUS_NUM,
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