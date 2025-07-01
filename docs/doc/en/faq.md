---
title: MaixCAM MaixPy FAQ (Frequently Asked Questions)
---

>! This page lists common questions and solutions related to MaixPy. If you encounter any issues, please search for answers here first.
> Additionally, there are other resources:
> * [MaixHub Discussion Forum](https://maixhub.com/discussion): A platform for discussions, with support for tip rewards.
> * [MaixPy Issues](https://github.com/sipeed/MaixPy/issues?q=): For source code-related issues.
> * [MaixCAM Hardware FAQ](https://wiki.sipeed.com/hardware/zh/maixcam/faq.html): Frequently asked questions about MaixCAM hardware.

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


## MaixVision MacOS can not launch

For macOS, since the developer account has not been used for signing during the early stages, you may encounter issues such as insufficient permissions or file corruption. 

Please refer to [this link](https://maixhub.com/discussion/100301) for a solution (run the command `sudo xattr -dr com.apple.quarantine /Applications/ApplicationName.app` in the terminal to remove this attribute).


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

## Why doesn’t the computer detect a serial port when connecting via USB to MaixCAM?

The USB port on the MaixCAM is a USB 2.0 interface of the chip, not a USB-to-serial interface, so it is normal for no serial port to appear when connected to a computer. 

How do you communicate without a USB-to-serial connection?
By default, the USB will simulate a USB network card. When you connect the USB to your computer, a virtual network card will appear. According to the instructions in the [Quick Start Guide](./README.md), you can use MaixVision to communicate with MaixCAM to run code, preview images, manage files, and other functions.

Additionally, since the USB simulates a network card, you can also use standard SSH software to connect to MaixCAM for communication. Alternatively, you can connect via WiFi and communicate within the same local network.

If you need to use the serial port, there are two situations:

1. **Serial communication with a computer**: You need to purchase any USB-to-serial module to connect the computer's USB port with the board's serial port (for MaixCAM, it's the UART0 pins A16 (TX) and A17 (RX), or you can use the TX and RX pins on the USB adapter board that comes with the MaixCAM package, which are also the A16 and A17 pins and are functionally equivalent).

2. **Serial communication with another MCU/SOC**: Directly connect MaixCAM's A16 (TX) and A17 (RX) to the MCU's RX and TX pins.


## Red Screen, Initialization Display Failed, Please Check FAQ

The message indicates that the display driver initialization failed.
As of July 2024, the underlying display driver for MaixCAM is initialized together with the camera driver. Therefore, this issue is most likely caused by a failure in the camera driver initialization.
To resolve this issue:
* Try updating to the latest system and install the latest runtime libraries (very important!!!). The runtime libraries need to work in conjunction with the system drivers, and version mismatches may cause errors. Updating to the latest system image and installing the latest runtime libraries should generally resolve the issue.
* Maybe multiple process try to occupy driver, easiest way is reboot.
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

MaixVision show  `no maix moudle` `"maix" is not accessed` or `Import "maix" could not be resolved`:

This error occurs because MaixVision's code hinting feature cannot find the `maix` module. It's important to understand that MaixVision's code hinting relies on the local Python packages on your computer, while the code execution depends on the Python packages on the device. To enable MaixVision's code hinting, you need to install Python and the `MaixPy` package on your computer. For more details, refer to the [MaixVision User Documentation](./basic/maixvision.md).

## MaixVision how to import from another .py file

Read documentation of [MaixVision](./basic/maixvision.md) carefully.

## MaixCAM starts very slowly, even exceeding 1 minute, or the screen flickers

This is mostly due to insufficient power supply. MaixCAM requires a voltage of around 5V and a current between 150mA and 500mA. If you encounter this issue, you can use a USB to TTL module to connect MaixCAM's serial port to a computer. You may see a message like `Card did not respond to voltage select! : -110`, indicating insufficient power supply. Simply switch to a more stable power supply to resolve the problem.

For MaixCAM, it draws 400mA during startup, 250mA in standby mode with the screen on, and 400mA~500mA when running AI models at full speed. Therefore, ensuring a stable power supply is very important!

## MaixCAM Black screen and not boot up, or stock in LOGO screen

Refer to [MaixCAM FAQ](https://wiki.sipeed.com/hardware/en/maixcam/faq.html)

## MaixVision Program Stuck on "start running ..."

When the MaixVision log output window prints the message `start running ...`, it indicates that the program has been sent to the device and has begun executing. What gets printed afterward depends on your program. For instance, if you call `print("hello")`, it will print `hello`. If your program doesn't include any print statements, then there will be no logs displayed.

So, the program isn't actually stuck; it's just that your program hasn't output anything, so no logs are shown. You can try adding `print("xxx")` in your code to generate output, which is the simplest way to debug your program.

## Why Does the Hardware Have 256MB of Memory, But Only 128MB is Available in the System?

The remaining memory is reserved for low-level drivers and the kernel, which are used for operating the camera, display, hardware encoding/decoding, NPU, and other drivers. You can check the memory used by these drivers (known as ION memory in CVITEK systems) by running `cat /sys/kernel/debug/ion/cvi_carveout_heap_dump/summary`. For other memory usage, you can run `cat /proc/meminfo`.

If you want to adjust the memory allocation, you would need to compile the system yourself and modify the `ION_SIZE` in the `memmap.py` file located in the `LicheeRV-Nano-Build/build/boards/sg200x/sg2002_licheervnano_sd/` directory(refer to [customize system doc](./pro/compile_os.md)).

## Why Am I Unable to Install the Runtime Library, and an Error "Request Failed" Is Displayed?

* Ensure that the device is successfully connected to the internet. You can try connecting to a different mobile hotspot.
* Verify that the system image you flashed is the latest version.
* If you see an error related to DNS resolution failure, it might be due to DNS settings issues on your network. You can try connecting to a different mobile hotspot or manually modify the DNS server settings in `/boot/resolv.conf` (modifying this file requires a reboot) and `/etc/resolv.conf` (modifying this file does not require a reboot, but rebooting will overwrite it with the contents of the former).
* Make sure you have purchased a genuine MaixCAM from Sipeed.
* Contact customer service, providing the system version and device_key (which can be found after disconnecting from MaixVision or, if you have a screen, in `System Settings -> System Information`).


Translation:

## Compile error: type not registered yet?

```
from ._maix.peripheral.key import add_default_listener
ImportError: arg(): could not convert default argument into a Python object (type not registered yet?). #define
```

The error indicates that an object has not been defined as a Python object. In MaixPy, this is usually caused by an issue with the order of automatic API generation. For example, if there is an API declared with `@maixpy` in `a.hpp`, and another API in `b.hpp` that uses a definition from `a.hpp` as a parameter, then `b.hpp` depends on `a.hpp`. However, the current MaixPy compilation script does not perform dependency scanning. To resolve this, you need to manually specify the scan order in the `components/maix/headers_priority.txt` file in the MaixPy project, ensuring that `a.hpp` is scanned before `b.hpp`.

## MaixVision Display Lag

The lag is typically due to using WiFi transmission. When the signal is weak or the image resolution is too high, delays can occur. Here are solutions to reduce lag:

* Switch to a wired connection; refer to the Quick Start Guide for details.
* Lower the image resolution by reducing the size of `img` in the code with `disp.show(img)`.

## Error Message When Running Application: Runtime error: mmf vi init failed

The error message indicates that camera initialization failed. Possible reasons include:1. The camera is occupied by another application. 2.The camera's ribbon cable may be loose. 3. The runtime library is not installed.
Solution Steps:
- Check if both the maixvision program and the board's built-in program are running at the same time. Ensure that only one program is using the camera. (Note: Usually, when maixvision is connected, the built-in program on the board will exit automatically.)
- Remove and reinsert the camera ribbon cable to ensure a proper connection.
- Update to the latest runtime library.

## When running the application, you see: maix multi-media driver released or maix multi-media driver destroyed

This is not an error message. It is a log message indicating that the multimedia framework is releasing resources, it is usually printed when the program exits.


## Why can't show Chinese charactors

By default only support English charactors, if you want to show Chinese, you need to change font, refer to [Custom fonts part of image basic operation](./vision/image_ops.md#Chinese-support-and-custom-fonts)

### Program Exit and Message: "app exit with code: 1, log in /maixapp/tmp/last_run.log"

This indicates that the program encountered an error and exited unexpectedly. You need to check the log to find the issue. 

#### How to Check the Logs:

- **Method 1**: View the `/maixapp/tmp/last_run.log` file immediately after the error:
  1. On MaixVision, run the script `MaixPy/examples/tools/show_last_run_log.py` to view the log.
  2. On an SSH terminal, use the command `cat /maixapp/tmp/last_run.log` to view the log.

- **Method 2**:
  - First, use MaixVision to connect to the device to exit any programs that are using the display or camera.
  - Then, connect to the device via SSH and enter the SSH terminal. For connection steps, refer to the [Linux Basics](./basic/linux_basic.md).
  - Manually run the program using the following commands:
    - If it's a Python program: `cd /maixapp/apps/xxx && python main.py`, where `xxx` is the ID of the application that encountered the error.
    - If it's not a Python program: `cd /maixapp/apps/xxx && ./xxx`, where `xxx` is the ID of the application that encountered the error.
  - Carefully examine the logs for any errors. Note that the error may not appear on the last line, so check the logs from the bottom upwards.

- **Method 3**: If the application is written in Python, use MaixVision to run the source code to view runtime errors and fix them. Again, be aware that the error may not appear on the last line, so check the logs carefully from the bottom upwards.

### Method 2:
If the application is written in Python, use **MaixVision** to run the source code directly, examine the runtime errors, and make corrections. Be aware that errors may not be at the last line, so inspect the logs carefully from the end upward.


### How to Read/Write to SD/TF Cards and Save Data to Them

MaixPy is based on Linux and standard Python 3. The operating system and file system both run on the SD/TF card, so reading and writing data is done through the file system.

You can use Python’s standard APIs to perform file operations. For example, to read a file:

```python
with open("/root/a.txt", "r") as f:
  content = f.read()
  print(content)
```

Similarly, other functions that are not covered in the documentation can be searched to check if they are included in Python’s built-in libraries, which you can call directly.

### Error: camera read timeout during image capture

This error might occur when the camera's image buffer does not contain new images, causing a timeout during image capture. In most cases, this happens because the image is read too quickly, or multiple camera channels are attempting to read simultaneously. For instance, if one camera channel is bound to an RTSP service while another thread tries to capture images from a second camera channel.

Solution: Catch the exception, wait for a short period, and then retry the capture. Example code:

```python
img = None
try:
    img = cam.read()
except:
    time.sleep_ms(10)
    continue
```

## VI_VENC_GetStream failed with 0xc0078012 during program runtime
This issue occurs because the program did not exit properly last time, causing the VENC module resources to not be released. As a result, the application cannot obtain the VENC resources when it starts again. The current solutions are:

1. Restart the system.

2. Turn off the MaixVision preview view or switch to the PNG stream.

Since this is a legacy issue at the underlying framework level, it can currently only be resolved at the application level. Efforts should be made to ensure that the program exits normally.


## How to uninstall the application

refer to [APP Usage Document](./basic/app.md).

## Why is the image so blurry, as if a Gaussian blur has been applied?

For the MaixCAM, the lens requires manual focusing. You can adjust the focus physically by twisting the lens.

## No module named 'lcd' or 'sensor': How to port OpenMV Code for Compatibility

MaixPy (v4) is compatible with both OpenMV and MaixPy-v1 code. All compatible modules are placed under the `maix.v1` module. For example, in OpenMV and MaixPy-v1:

```python
import lcd, sensor
```

In MaixPy (v4), you should write:

```python
from maix.v1 import lcd, sensor
```

Or, to import all compatible modules at once (not recommended due to reduced code readability):

```python
from maix.v1 import *
import lcd, sensor
```

The latest version of MaixPy provides a compatibility layer for OpenMV/MaixPy-v1, built on top of the new API. The source code is available at: [https://github.com/sipeed/MaixPy/tree/main/maix/v1](https://github.com/sipeed/MaixPy/tree/main/maix/v1).

Therefore, **it is highly recommended to upgrade to the new MaixPy API**, which offers richer features and better performance.

If you must use the old API and find that a specific function is not supported by the official compatibility layer, you can try modifying the source code mentioned above to add support by calling the new API underneath. Then, consider contributing your changes to the community at [https://github.com/sipeed/MaixPy](https://github.com/sipeed/MaixPy). For contribution guidelines, refer to the [MaixPy Contribution Documentation](./source_code/contribute.md).


## Where Are Photos and Videos Taken by the Built-in Camera App on MaixCAM Stored, and How to Export Them to a Computer

Photos and videos taken using MaixCAM’s built-in **Camera** app can be viewed in the **Gallery** app. You can see the file path of a photo by tapping the `Info` button.

To export the files to your computer, you can use the [MaixVision file manager feature](./basic/maixvision.md) or other file transfer tools such as `scp` or `WinSCP`.


## No Network, Is There an Offline Version of the Documentation?

Yes.

An offline HTML version of the documentation is provided. Go to the [MaixPy release page](https://github.com/sipeed/MaixPy/releases) and download the file named `maixpy_v*.*.*_doc.zip`.

After extracting the file, you will get a `html` folder. Make sure `Python` is installed on your computer, then run the following command: `chmod +x ./view_doc.sh && ./view_doc.sh` (for Linux/MacOS) or `view_doc.bat` (for Windows).

After that, open `http://<your_computer_IP>:8000/maixpy/index.html` in your browser to view the documentation offline.

Additionally, if you just want to save a single page for offline viewing, you can press `Ctrl + P` on that page and select "Print as PDF" to save the page as a local PDF file.

