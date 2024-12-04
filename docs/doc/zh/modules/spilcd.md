---
title: MaixCAM MaixPy SPI LCD 屏幕
update:
  - date: 2024-12-02
    author: 916BGAI
    version: 1.0.0
    content: 初版文档
---

## 简介

`MaixCAM` 配备三路硬件SPI接口，可以通过 SPI 接口连接并驱动 LCD 屏幕。

> 目前仅支持通过硬件 SPI 驱动 LCD 屏幕，且需要修改 Linux 内核，不支持软件 SPI。

> **注意：** 阅读本文档需要具备一定的内核编译、内核配置和内核驱动开发的知识。

## 使用 ST7789 屏幕

这里以 `ST7789` 驱动的 LCD 屏为例。

### 获取 LicheeRV-Nano-Build 源代码

`MaixCAM` 使用的基础系统为 [https://github.com/sipeed/LicheeRV-Nano-Build](https://github.com/sipeed/LicheeRV-Nano-Build)。

首先拉去最新的源码，按照 [README](https://github.com/sipeed/LicheeRV-Nano-Build/blob/main/README.md) 中的方法完成系统的构建。

### 修改 linux 内核

首先修改内核配置，开启 `FB_TFT` 支持，可以在 LicheeRV-Nano-Build 根目录执行 `menuconfig_kernel` 后使用文本界面菜单进行配置，配置项位于:

`Device Drivers -> Staging drivers -> Support for small TFT LCD display modules`

选择你所使用的屏幕驱动，这里选择 `ST7789` 驱动，并将其编译为内核模块：

`<M>   FB driver for the ST7789 LCD Controller`

> 也可以直接修改配置文件 `build/boards/sg200x/sg2002_licheervnano_sd/linux/sg2002_licheervnano_sd_defconfig` 。
> 添加 `CONFIG_FB_TFT=y` 和 `CONFIG_FB_TFT_ST7789=m` 即可。

### 修改设备树

修改设备树文件 `build/boards/sg200x/sg2002_licheervnano_sd/dts_riscv/sg2002_licheervnano_sd.dts`

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
这里使用的是 `SPI2`，由于 Wi-Fi 模块将 `SPI2` 引脚复用为 `SDIO`，因此我们需要修改引脚的复用功能，修改方法见下面的例程。修改后，Wi-Fi 功能将不可用。

修改完设备树后，重新编译镜像，并根据 [为 MaixCAM 编译系统](https://wiki.sipeed.com/maixpy/doc/zh/pro/compile_os.html) 的方法生成适用于 MaixCAM 的镜像。

### 测试屏幕

maixpy 例程:

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
- 首先移除 aic8800 驱动模块防止其占用 SDIO 总线影响屏幕驱动。
- 修改引脚复用，将对应引脚映射为 SPI 功能，使用 `pinmap` 修改引脚复用的具体方法可以查看 [MaixPy Pinmap 使用介绍](https://wiki.sipeed.com/maixpy/doc/zh/peripheral/pinmap.html)。
- 然后使用 `insmod` 加载屏幕驱动模块即可，查看系统日志，可以看到驱动加载成功。在 /dev 目录下也可以找到生成的 `fb0` 设备。

```bash
[ 1029.909582] fb_st7789: module is from the staging directory, the quality is unknown, you have been warned.
[ 1029.911792] fb_st7789 spi2.0: fbtft_property_value: buswidth = 8
[ 1029.911814] fb_st7789 spi2.0: fbtft_property_value: debug = 0
[ 1029.911828] fb_st7789 spi2.0: fbtft_property_value: rotate = 90
[ 1029.911842] fb_st7789 spi2.0: fbtft_property_value: fps = 60
[ 1030.753696] graphics fb0: fb_st7789 frame buffer, 320x240, 150 KiB video memory, 4 KiB buffer memory, fps=62, spi2.0 at 80 MHz
```

- 接下来使用屏幕就很简单了，只需要在创建 `Display` 实例时指定对应的 `fb` 设备即可。然后就可以按照正常方法使用 `SPI` 屏幕了 （[MaixPy 屏幕使用](https://wiki.sipeed.com/maixpy/doc/zh/vision/display.html)）。

```python
disp = display.Display(device="/dev/fb0")
```
## 注意事项
### 屏幕时序问题
不同屏幕的初始化时序可能有所不同。例如，`ST7789` 包括 `ST7789V1`、`ST7789V2` 等不同版本，每个版本的初始化时序可能不同，[LicheeRV-Nano-Build](https://github.com/sipeed/LicheeRV-Nano-Build) 仓库里驱动的不能保证在每个 st7789 屏幕上都能正常使用。具体屏幕的初始化时序可以联系商家获取，并修改 `LicheeRV-Nano-Build/linux_5.10/drivers/staging/fbtft/fb_st7789.c` 中的 `init_display` 函数。

### 引脚复用
在使用 `pinmap` 设置引脚复用时，确保与设备树中的引脚配置一致。一般来说 SPI 屏的 `dc` 引脚和 `reset` 引脚不会和硬件绑定，可以在设备树中任意指定，选择 `MaixCAM` 中未被占用的引脚即可，然后在 `pinmap` 时将其映射为 GPIO 功能。

### 驱动其他屏幕
目前，`fb` 设备已测试了 `st7789` 屏幕驱动。`linux_5.10/drivers/staging/fbtft` 中还有其他屏幕驱动可供测试。如遇问题，欢迎提交 `commit` 或 `PR` 做出贡献。