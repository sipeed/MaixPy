---
title: MaixCAM MaixPy Screen Usage
update:

  - date: 2024-03-31
    author: neucrack
    version: 1.0.0
    content: Initial document
---
## Introduction

MaixPy provides the `display` module, which can display images on the screen, and can also send images to MaixVision for display, facilitating debugging and development.

## API Documentation

This document introduces commonly used methods. For more APIs, please refer to the [display](/api/maix/display.html) section of the API documentation.

## Using the Screen

* Import the `display` module:
```python
from maix import display
```

* Create a `Display` object:
```python
disp = display.Display()
```

* Display an image:
```python
disp.show(img)
```

Here, the `img` object is a `maix.image.Image` object, which can be obtained through the `read` method of the `camera` module, or loaded from an image file in the file system using the `load` method of the `image` module, or created as a blank image using the `Image` class of the `image` module.

For example:
```python
from maix import image, display

disp = display.Display()
img = image.load("/root/dog.jpg")
disp.show(img)
```
Here, you need to transfer the `dog.jpg` file to the `/root` directory on the device first.

Display text:
```python
from maix import image, display

disp = display.Display()
img = image.Image(320, 240)
img.draw_rect(0, 0, disp.width(), disp.height(), color=image.Color.from_rgb(255, 0, 0), thickness=-1)
img.draw_rect(10, 10, 100, 100, color=image.Color.from_rgb(255, 0, 0))
img.draw_string(10, 10, "Hello MaixPy!", color=image.Color.from_rgb(255, 255, 255))
disp.show(img)
```

Read an image from the camera and display it:
```python
from maix import camera, display, app

disp = display.Display()
cam = camera.Camera(320, 240)
while not app.need_exit():
    img = cam.read()
    disp.show(img)
```

> Here, `while not app.need_exit():` is used to facilitate exiting the loop when the `app.set_exit_flag()` method is called elsewhere.

## Adjusting Backlight Brightness

You can manually adjust the backlight brightness in the system's "Settings" app. If you want to adjust the backlight brightness programmatically, you can use the `set_backlight` method, with the parameter being the brightness percentage, ranging from 0 to 100:
```python
disp.set_backlight(50)
```

Note that when the program exits and returns to the app selection interface, the backlight brightness will automatically revert to the system setting.

If the brightness is set to `100%` and still feels dim, you can try modifying the `disp_max_backlight=50` option in the `/boot/board` file to a larger value. When `disp_max_backlight=100` and `disp.set_backlight(100)` are set, the hardware backlight control pin outputs a 100% duty cycle, which is a high level. The final duty cycle output to the hardware is calculated as:  
`set_backlight value` * `disp_max_backlight`.  

**Note**: Increasing the maximum brightness limit will lead to higher power consumption and heat generation. Adjust it reasonably based on your actual needs and avoid blindly maxing out the brightness.

## Displaying on MaixVision

When running code in MaixVision, images can be displayed on MaixVision for easier debugging and development.

When calling the `show` method, the image will be automatically compressed and sent to MaixVision for display.

Of course, if you don't have a screen, or to save memory by not initializing the screen, you can also directly call the `send_to_maixvision` method of the `maix.display` object to send the image to MaixVision for display.
```python
from maix import image,display

from maix import image,display

img = image.Image(320, 240)
disp = display.Display()

img.draw_rect(0, 0, img.width(), img.height(), color=image.Color.from_rgb(255, 0, 0), thickness=-1)
img.draw_rect(10, 10, 100, 100, color=image.Color.from_rgb(255, 0, 0))
img.draw_string(10, 10, "Hello MaixPy!", color=image.Color.from_rgb(255, 255, 255))
display.send_to_maixvision(img)
```

## Replacing with Other Screen Models

If you wish to switch to a screen of a different size, you can consult and purchase from the [store](https://wiki.sipeed.com/store).

For MaixCAM, currently, there are 4 types of screens and 1 type of MIPI to HDMI module supported:
* 2.3-inch 552x368 resolution capacitive touch screen: The default screen that comes with MaixCAM.
* 2.4-inch 640x480 resolution capacitive touch screen: The default screen that comes with MaixCAM-Pro.
* 5-inch 854x480 resolution non-touch screen: Note that this is a non-touch screen, similar in size to a mobile phone screen.
* 7-inch 1280x800 resolution capacitive touch screen: A large 7-inch screen, suitable for scenarios requiring a fixed screen display.
* LT9611 (MIPI to HDMI module) supports various resolutions including 1280x720, suitable for driving various HDMI screens.

The image refresh time difference between different screens is about 1-5 milliseconds, which is not significant; the main difference lies in the image resolution, which affects image processing time.

When replacing the screen, you must also **modify the configuration file**; otherwise, mismatched refresh timing could **cause screen burn-in** (leaving a ghost image on the screen). It’s important to follow the steps strictly as outlined below. If screen burn-in occurs, don’t panic; powering off and leaving it overnight usually resolves the issue.

* Follow the system burning documentation to burn the system. Once completed, a USB drive will appear.
* Open the USB drive, and you will see a `board` file.
* Edit the `board` file, modifying the `pannel` key value as follows:
  * 2.3-inch (MaixCAM default screen): `st7701_hd228001c31`.
  * 2.4-inch (MaixCAM-Pro default screen): `st7701_lct024bsi20`.
  * 5-inch: `st7701_dxq5d0019_V0`, with the earlier (2023) test screen being `st7701_dxq5d0019b480854`.
  * 7-inch: `mtd700920b`, with the earlier (2023) test screen being `zct2133v1`.
  * LT9611 (MIPI to HDMI module):
    * Wiring:
      * LT9611 I2C <---> MaixCAM I2C5
      * LT9611 MIPI IN <---> MaixCAM MIPI OUT
    * Supported configurations:
      * `lt9611_1280x720_60hz`: 1280x720 60Hz
      * `lt9611_1024x768_60hz`: 1024x768 60Hz
      * `lt9611_640x480_60hz`: 640x480 60Hz
      * `lt9611_552x368_60hz`: 552x368 60Hz
* Save the `board` file, and **click to eject the USB drive**—do not just disconnect the power, or the file may be lost.
* Press the board's `reset` button, or power cycle to restart.

The above method is the safest, ensuring the screen model is set correctly before powering on. If you have already burned the system, you can also modify the system’s `/boot/board` file and then reboot.
> If you use earlier system and binary program(< 2024.11.25), you may have to change `uEnv.txt` too.

