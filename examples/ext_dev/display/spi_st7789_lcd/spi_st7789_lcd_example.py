from maix import pinmap, display, image, app
import subprocess

# Please read the MaixPy SPI LCD Screen documentation (https://wiki.sipeed.com/maixpy/doc/zh/modules/spilcd.html) first.

try:
    result = subprocess.run(['lsmod'], capture_output=True, text=True, check=True)
    if "aic8800_bsp" in result.stdout:
        subprocess.run(['rmmod', 'aic8800_fdrv'], check=True)
        subprocess.run(['rmmod', 'aic8800_bsp'], check=True)
    else:
        print(f"aic8800 module is not currently loaded, skipping remove.")
except Exception as e:
    print(e)

pinmap.set_pin_function("P18", "SPI2_CS")
pinmap.set_pin_function("P22", "SPI2_MOSI")
pinmap.set_pin_function("P23", "SPI2_SCK")
pinmap.set_pin_function("P20", "GPIOP20")
pinmap.set_pin_function("P21", "GPIOP21")

try:
    result = subprocess.run(['lsmod'], capture_output=True, text=True, check=True)
    if "fb_st7789" in result.stdout:
        print(f"module is already loaded, skipping loading.")
    else:
        subprocess.run(['insmod', '/mnt/system/ko/fb_st7789.ko'], check=True)
        print(f"load fb_st7789 success.")
except Exception as e:
    print(e)

disp = display.Display(device="/dev/fb0")
print("display init done")
print(f"display size: {disp.width()}x{disp.height()}")

y = 0
while not app.need_exit():
    img = image.Image(disp.width(), disp.height(), image.Format.FMT_RGB888)
    img.draw_rect(0, y, image.string_size("Hello, MaixPy!", scale=2).width() + 10, 80, color=image.Color.from_rgb(255, 0, 0), thickness=-1)
    img.draw_string(4, y + 4, "Hello, MaixPy!", color=image.Color.from_rgb(255, 255, 255), scale=2)

    disp.show(img)

    y = (y + 1) % disp.height()