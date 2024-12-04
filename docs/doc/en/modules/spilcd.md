---
title: MaixCAM MaixPy SPI LCD Screen
update:
  - date: 2024-12-02
    author: 916BGAI
    version: 1.0.0
    content: Initial document
---

## Introduction

`MaixCAM` is equipped with three hardware SPI interfaces, allowing you to connect and drive an LCD screen via the SPI interface.

> Currently, only hardware SPI is supported for driving the LCD screen, and it requires modification to the Linux kernel. Software SPI is not supported.

> **Note：** Reading this document requires a certain level of knowledge in kernel compilation, kernel configuration, and kernel driver development.

## Using the ST7789 Screen

This section uses the LCD screen driven by `ST7789` as an example.

### Get the LicheeRV-Nano-Build Source Code

The base system used by `MaixCAM` is [https://github.com/sipeed/LicheeRV-Nano-Build](https://github.com/sipeed/LicheeRV-Nano-Build).

First, pull the latest source code and follow the instructions in the [README](https://github.com/sipeed/LicheeRV-Nano-Build/blob/main/README.md) to build the system.

### Modify the Linux Kernel

First, modify the kernel configuration to enable `FB_TFT` support. You can execute `menuconfig_kernel` in the root directory of LicheeRV-Nano-Build, then use the text-based menu interface to configure it. The configuration option is located at:

`Device Drivers -> Staging drivers -> Support for small TFT LCD display modules`

Select the driver for the screen you are using; in this case, choose the `ST7789` driver, and compile it as a kernel module:

`<M>   FB driver for the ST7789 LCD Controller`

> Alternatively, you can directly modify the configuration file `build/boards/sg200x/sg2002_licheervnano_sd/linux/sg2002_licheervnano_sd_defconfig` 
> by adding `CONFIG_FB_TFT=y` and `CONFIG_FB_TFT_ST7789=m`.

### Modify the Device Tree

Modify the device tree file `build/boards/sg200x/sg2002_licheervnano_sd/dts_riscv/sg2002_licheervnano_sd.dts`.

```c
&spi2 {
	status = "okay";
        /delete-node/ spidev@0;
        st7789: st7789@0{
		compatible = "sitronix,st7789";
		reg = <0>;
		status = "okay";
		spi-max-frequency = <80000000>;
		spi-cpol;
		spi-cpha;
		rotate = <90>;
		fps = <60>;
		rgb;
		buswidth = <8>;
		dc = <&porte 20 GPIO_ACTIVE_HIGH>;
		reset = <&porte 21 GPIO_ACTIVE_LOW>;
		debug = <0>;
	};
};
```
This example uses `SPI2`. Since the Wi-Fi module reuses the `SPI2` pins for `SDIO`, we need to modify the pin multiplexing. The method for modification is shown in the example below. After modification, the Wi-Fi functionality will be unavailable.

After modifying the device tree, recompile the image and generate the MaixCAM-compatible image following the instructions in the [Compiling a System for MaixCAM](https://wiki.sipeed.com/maixpy/doc/en/pro/compile_os.html) guide.

### Test the Screen

maixpy example:

```python
from maix import pinmap, display, image, app
import subprocess

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
```
- First, remove the aic8800 driver module to prevent it from occupying the SDIO bus, which could interfere with the screen driver.
- Modify the pin multiplexing, mapping the corresponding pins to SPI functions. For detailed instructions on how to modify the pin multiplexing using pinmap, refer to [Using PINMAP in MaixCAM](https://wiki.sipeed.com/maixpy/doc/en/peripheral/pinmap.html).
- Then, use `insmod` to load the screen driver module. Check the system logs to confirm that the driver has been successfully loaded. You can also find the generated `fb0` device in the /dev directory.

```bash
[ 1029.909582] fb_st7789: module is from the staging directory, the quality is unknown, you have been warned.
[ 1029.911792] fb_st7789 spi2.0: fbtft_property_value: buswidth = 8
[ 1029.911814] fb_st7789 spi2.0: fbtft_property_value: debug = 0
[ 1029.911828] fb_st7789 spi2.0: fbtft_property_value: rotate = 90
[ 1029.911842] fb_st7789 spi2.0: fbtft_property_value: fps = 60
[ 1030.753696] graphics fb0: fb_st7789 frame buffer, 320x240, 150 KiB video memory, 4 KiB buffer memory, fps=62, spi2.0 at 80 MHz
```

- Using the screen is straightforward. Simply specify the corresponding `fb` device when creating the `Display` instance. After that, you can use the `SPI` screen in the usual way ([MaixPy Screen Usage](https://wiki.sipeed.com/maixpy/doc/en/vision/display.html)).

```python
disp = display.Display(device="/dev/fb0")
```
## Notes
### Screen Timing Issues
The initialization timing for different screens may vary. For example, the `ST7789` includes different versions such as `ST7789V1` and `ST7789V2`, each with potentially different initialization timings. The drivers in the [LicheeRV-Nano-Build](https://github.com/sipeed/LicheeRV-Nano-Build) repository cannot guarantee that they will work properly with every st7789 screen. You can contact the supplier to obtain the specific initialization sequence for your screen and modify the `init_display` function in `LicheeRV-Nano-Build/linux_5.10/drivers/staging/fbtft/fb_st7789.c`.

### Pin Multiplexing
When using `pinmap` to set pin multiplexing, ensure that it matches the pin configuration in the device tree. Generally, the `dc` and `reset` pins for SPI screens are not hardware-bound, so you can specify them arbitrarily in the device tree. Simply choose pins that are not in use on the `MaixCAM` board, and then map them to GPIO functions using `pinmap`.

### Drive Other Screens
Currently, the `fb` device has tested the `st7789` screen driver. There are other screen drivers available for testing in `linux_5.10/drivers/staging/fbtft`. If you encounter any issues, feel free to submit a `commit` or a `PR` to contribute.