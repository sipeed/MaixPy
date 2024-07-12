---
title: MaixPy FAQ (Frequently Asked Questions)
---

This page lists common questions and solutions related to MaixPy. If you encounter any issues, please search for answers here first.
If you cannot find an answer on this page, you can post your question with detailed steps on the [MaixHub Discussion Forum](https://maixhub.com/discussion).

If you use MaixCAM, you can also refer to [MaixCAM FAQ](https://wiki.sipeed.com/hardware/zh/maixcam/faq.html)

## MaixVision cannot find the device?

First, confirm whether the connection method is WiFi or USB cable.
**WiFi**:
* Ensure that WiFi is correctly connected and has obtained an IP address. You can view the `ip` in `Settings -> Device Info` or `Settings -> WiFi`.

**USB Cable**:
* Ensure that the device is connected to the computer via a Type-C data cable, and the device is powered on and has entered the function selection interface.
* Ensure that the device driver is installed:
  * On Windows, check if there is a USB virtual network adapter device in `Device Manager`. If there is an exclamation mark, it means the driver is not installed properly. Follow the instructions in [Quick Start](./README.md) to install the driver.
  * On Linux, you can check if there is a `usb0` device by running `ifconfig` or `ip addr`, or check all USB devices with `lsusb`. Linux already includes the driver, so if the device is not recognized, check the hardware connection, ensure the device system is up-to-date, and ensure the device has booted up properly.
  * On macOS, follow the same steps as Linux.
* Additionally, check the quality of the USB cable and try using a high-quality cable.
* Additionally, check the quality of the computer's USB port. For example, some small form factor PCs have poor EMI design on their USB ports, and connecting a good quality USB hub may allow the device to work. You can also try a different USB port or a different computer.

## MaixVision camera example shows choppy video

The default GC4653 camera has a maximum frame rate of 30 frames per second (FPS). Under normal circumstances, the MaixVision display should not appear choppy to the naked eye. If choppiness occurs, first consider transmission issues:
* Check the network connection quality, such as WiFi.
* If using a USB connection, check the USB cable quality, computer USB port quality, and try using a different computer, USB port, or USB cable for comparison.

## What is the difference between MaixPy v4 and v1/v3?

* MaixPy v4 uses the Python language and is the culmination of the experiences from v1 and v3, offering better supporting software and ecosystem, more features, simpler usage, and more comprehensive documentation. While the hardware has significant improvements, the pricing is even more affordable compared to the other two versions. Additionally, it provides compatibility with the K210 user experience and API, making it easier for users to migrate quickly from v1 to v4.
* v1 used the Micropython language and had many limitations, such as limited third-party library support. Additionally, due to the hardware performance limitations of the Maix-I (K210), there was not enough memory, limited AI model support, and lack of hardware acceleration for many codecs.
* v3 also used the Python language and was based on the Maix-II-Dock (v831) hardware. However, the hardware had limited AI model support, and the Allwinner ecosystem was not open enough, with an incomplete API. This version was only intended for use with the Maix-II-Dock (v831) and will not receive further updates.

## Does MaixPy currently only support MaixCAM, or can it work with other boards using the same chipset?

MaixPy currently only supports the MaixCAM series of boards. Other boards using the same chipset, including Sipeed's boards like the LicheeRV-Nano, are not supported. It is strongly recommended not to attempt using MaixPy with other boards, as it may result in device damage (such as smoke or screen burn), for which you will be solely responsible.

In the future, Sipeed's Maix series of products will continue to be supported by MaixPy. If you have any needs that cannot be met by MaixCAM, you can post your requirements on the [MaixHub Discussion Forum](https://maixhub.com/discussion) or send an email to support@sipeed.com.

## Can I use a camera or screen other than the officially bundled ones?

It is not recommended to use cameras or screens other than the officially bundled ones, unless you have sufficient software and hardware knowledge and experience. Otherwise, it may result in device damage.

The officially bundled accessories have been fine-tuned for both software and hardware, ensuring the best performance and allowing for out-of-the-box usage. Other accessories may have different interfaces, drivers, and software, requiring you to calibrate them yourself, which is an extremely complex process.

However, if you are an expert, we welcome you to submit a pull request!

## Model running error: cvimodel built for xxxcv181x CANNOT run on platform cv181x.

Failure to parse the model file is generally caused by file corruption. Ensure that your model file is not damaged. For example:
* Editing a binary file with an editor caused the file to become corrupted. For example, opening a `cvimodel` file with MaixVision can corrupt the binary file due to MaixVision's auto-save feature. Therefore, do not open and save binary files with text editors like MaixVision (this issue will be fixed in a future update of MaixVision by removing the auto-save feature).
* If it was downloaded from the internet, make sure the download was not corrupted. Typically, files on the internet provide sha256sum/md5 checksums. After downloading, you can compare these values; for specific methods, please search online or ask ChatGPT.
* If it comes from a compressed archive, ensure that the decompression process was error-free. You can decompress the archive again to make sure there were no errors in the process.
* Ensure that the file was not damaged during the transfer to the device. You can compare the sha256sum values of the file on the device and on your computer; for specific methods, please search online or ask ChatGPT.


## Power-on Black Screen, No Display on the Screen

Refer to [MaixCAM FAQ](https://wiki.sipeed.com/hardware/zh/maixcam/faq.html)

## Red Screen, Initialization Display Failed, Please Check FAQ

The message indicates that the display driver initialization failed.
As of July 2024, the underlying display driver for MaixCAM is initialized together with the camera driver. Therefore, this issue is most likely caused by a failure in the camera driver initialization.
To resolve this issue:
* Try updating to the latest system and install the latest runtime libraries (very important!!!). The runtime libraries need to work in conjunction with the system drivers, and version mismatches may cause errors. Updating to the latest system image and installing the latest runtime libraries should generally resolve the issue.
* Check for hardware connection issues with the camera. Ensure that the camera is properly connected and not damaged.

## What are the differences between Runtime, MaixPy, and system image? Which one should I upgrade?

* **Runtime** is the runtime environment. Many system functions depend on it, including MaixPy. If you encounter the problem of being unable to run the program, first check and update it online.

* The system image includes the basic operating system, hardware drivers, built-in applications, and MaixPy firmware, etc. It is the basic environment. It is best to keep it up to date, especially in the [Release](https://github.com/sipeed/MaixPy/releases) page. If the version update mentions that the system has been updated, it is strongly recommended to update the system, because some MaixPy functions may depend on the drivers in the system.
> Updating the system will format all previous data. Please back up useful data in the device system before updating.

* **MaixPy** is a dependent library for running the MaixPy program. If you do not need to update the system function, and the update log does not mention that the system has important updates such as drivers, you can update MaixPy alone.


## Error Loading MUD Model File: *****.cvimodel not exists, load model failed

* Check if the .mud file you are trying to load really exists on the device (note, it should be on the device, not on the computer, it needs to be transferred to the device).
* Verify that the model path you wrote is correct.
* If you have changed the file name, note that the MUD file is a model description file and can be edited with a text editor. The actual model file is the .cvimodel file (for MaixCAM). The .mud file specifies the file name and path of the .cvimodel. Therefore, if you have changed the file name of `.cvimodel`, you also need to modify the `model` path in the `.mud` file. For example, here is the mud file for the Yolov5 model:
```ini
[basic]
type = cvimodel
model = yolov5s_224_int8.cvimodel

[extra]
model_type = yolov5
input_type = rgb
mean = 0, 0, 0
scale = 0.00392156862745098, 0.00392156862745098, 0.00392156862745098
anchors = 10,13, 16,30, 33,23, 30,61, 62,45, 59,119, 116,90, 156,198, 373,326
labels = person, bicycle, car, motorcycle, airplane, bus, train, truck, boat, traffic light, fire hydrant, stop sign, parking meter, bench, bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe, backpack, umbrella, handbag, tie, suitcase, frisbee, skis, snowboard, sports ball, kite, baseball bat, baseball glove, skateboard, surfboard, tennis racket, bottle, wine glass, cup, fork, knife, spoon, bowl, banana, apple, sandwich, orange, broccoli, carrot, hot dog, pizza, donut, cake, chair, couch, potted plant, bed, dining table, toilet, tv, laptop, mouse, remote, keyboard, cell phone, microwave, oven, toaster, sink, refrigerator, book, clock, vase, scissors, teddy bear, hair dryer, toothbrush
```
Here, the `model` is specified as the `yolov5s_224_int8.cvimodel` file relative to the directory of this `.mud` file. If you have changed `yolov5s_224_int8.cvimodel` to another name, you need to update it here as well.


## MaixVision Shows Red Wavy Line on `import maix`

This error occurs because MaixVision's code hinting feature cannot find the `maix` module. It's important to understand that MaixVision's code hinting relies on the local Python packages on your computer, while the code execution depends on the Python packages on the device. To enable MaixVision's code hinting, you need to install Python and the `MaixPy` package on your computer. For more details, refer to the [MaixVision User Documentation](./basic/maixvision.md).
