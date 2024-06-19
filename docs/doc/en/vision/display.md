---
title: MaixPy Screen Usage
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

## Displaying on MaixVision

When running code in MaixVision, images can be displayed on MaixVision for easier debugging and development.

When calling the `show` method, the image will be automatically compressed and sent to MaixVision for display.

Of course, if you don't have a screen, or to save memory by not initializing the screen, you can also directly call the `send_to_maixvision` method of the `image.Image` object to send the image to MaixVision for display.
```python
from maix import image

img = image.Image(320, 240)
img.draw_rect(0, 0, img.width(), img.height(), color=image.Color.from_rgb(255, 0, 0), thickness=-1)
img.draw_rect(10, 10, 100, 100, color=image.Color.from_rgb(255, 0, 0))
img.draw_string(10, 10, "Hello MaixPy!", color=image.Color.from_rgb(255, 255, 255))
img.send_to_maixvision()
```
