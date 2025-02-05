---
title: MaixVision -- MaixCAM MaixPy Programming IDE + Graphical Block Programming
---

## Introduction

[MaixVision](https://wiki.sipeed.com/maixvision) is a development tool specifically designed for the Maix ecosystem, supporting MaixPy programming and graphical block programming. It allows for online operation and debugging, real-time image preview, and synchronizing images from device displays, which is convenient for debugging and development.

It also supports packaging and installing applications on devices, allowing users to easily generate and install applications with one click.

In addition, it integrates several handy tools for development, such as file management, threshold editor, QR code generator, and more.

## Download

Visit the [MaixVision homepage](https://wiki.sipeed.com/maixvision) to download.


## Using MaixPy Programming and Online Running

Follow the steps in [Quick Start](../README.md) to connect your device, and you can easily use MaixPy programming and run it online.

## Real-time Image Preview

MaixPy provides a `display` module that can show images on the screen. Also, when the `show` method of the `display` module is called, it sends the image to be displayed on MaixVision, for example:
```python
from maix import display, camera

cam = camera.Camera(640, 480)
disp = display.Display()
while 1:
    disp.show(cam.read())
```

Here we use the camera to capture an image, then display it on the screen using the `disp.show()` method, and also send it to MaixVision for display.

When we click the 'pause' button in the top right corner, it will stop sending images to MaixVision.


## Code Auto Completion

Code suggestions depend on local Python packages installed on your computer. To enable code suggestions, you need to install Python on your computer and the required Python packages.
> If it is not installed, a red underlined wavy line error prompt will be displayed. The code can still run normally, but there will be no code completion prompt.

* To install Python, visit the [Python official website](https://python.org/).
* To install the required packages, for MaixPy, for instance, you need to install the MaixPy package on your computer using `pip install MaixPy`. If `MaixPy` gets updated, you should update it on both your computer and device. On your computer, manually execute `pip install MaixPy -U` in the terminal. For device updates, update directly in the `Settings` application.
> Users in China can use a local mirror `pip install -i https://pypi.tuna.tsinghua.edu.cn/simple MaixPy`.
* Restart MaixVision to see the code suggestions.
> If suggestions still do not appear, you can manually set the path to the Python executable in settings and restart.

>! Note that installing Python packages on your computer is just for code suggestions. The actual code runs on the device (development board), and the device must also have the corresponding packages to run properly.


> Additionally, while you have the MaixPy package installed on your computer, due to our limited resources, we cannot guarantee that you can directly use the Maix package in your computer's Python. Please run it on supported devices.


In addition, in addition to the MaixPy package, other code hints, such as `numpy/opencv`, also need to be installed on the computer to implement code hints.

## Single file and project (multiple py file projects/modularization)

When writing code, there are generally two modes, executing a single file, or executing a complete project (containing multiple py files or other resource files).
* **Single file mode**: MaixVision creates or opens a file in the `.py` format, and clicks Run in the lower left corner after editing to execute the code.
* **Project (multiple files) mode**:
  * Create an empty folder in the system file manager, and MaixVision clicks `Open folder/project` to open this empty folder.
  * Create a main program entry of `main.py` (the name must be `main.py`). If `main.py` wants to reference other `.py` files, create a `.py` file in the project folder, such as `a.py`
  ```python
  def say_hello():
  print("hello from module a")
  ```
  * Reference in `main.py`
  ```python
  from a import say_hello
  say_hello()
  ```
  * Run the project, click the `Run Project` button in the lower left corner to automatically package the entire project and send it to the device for running.
  * If you have opened a folder/project and still want to run a file separately, you can open the file you want to run, and then click the `Run Current File` in the lower left corner to send only the current file to the device for running. Note that other files will not be sent to the device, so do not reference other `.py` files.


## Calculating the Image Histogram

In the previous step, we could see the image in real-time in MaixVision. By selecting an area with the mouse, we can view the histogram for that area at the bottom of the screen, displaying different color channels.

This feature is helpful when finding suitable parameters for some image processing algorithms.

## Distinguishing Between `Device File System` and `Computer File System`

Here we have an important concept to grasp: **distinguish between the `Device File System` and the `Computer File System`**.
* **Computer File System**: Operates on the computer. Opening a file or project in MaixVision accesses files on the computer, and saving is automatically done to the computer's file system.
* **Device File System**: The program sends the code to the device for execution, so the files used in the code are read from the device's file system.

A common issue is when students save a file on the computer, such as `D:\data\a.jpg`, and then use this file on the device with `img = image.load("D:\data\a.jpg")`. Naturally, the file cannot be found because the device does not have `D:\data\a.jpg`.

For specifics on how to send files from the computer to the device, refer to the following section.


## Transferring Files to the Device

First, connect to the device, then click the button to browse the device file system, as shown below. Then you can upload files to the device or download files to the computer.

![maixvision_browser2](../../assets/maixvision_browser2.jpg)

![maixvision_browser](../../assets/maixvision_browser.jpg)

.. details:: Alternatively, other tools can be used, click to expand
    First, know the device's IP address or name, which MaixVision can find, or see in the device's `Settings->System Information`, such as `maixcam-xxxx.local` or `192.168.0.123`.
    The username and password are `root`, using the `SFTP` protocol for file transfer, and the port number is `22`.

    There are many useful tools available for different systems:

    ### Windows

    Use [WinSCP](https://winscp.net/eng/index.php) or [FileZilla](https://filezilla-project.org/) to connect to the device and transfer files, choosing the `SFTP` protocol and entering the device and account information to connect.

    Specific instructions can be searched online.

    ### Linux

    In the terminal, use the `scp` command to transfer files to the device, such as:

    ```bash
    scp /path/to/your/file.py root@maixcam-xxxx.local:/root
    ```

    ### Mac

    * **Method 1**: In the terminal, use the `scp` command to transfer files to the device, such as:
    ```bash
    scp /path/to/your/file.py root@maixcam-xxxx.local:/root
    ```

    * **Method 2**: Use [FileZilla](https://filezilla-project.org/) or other tools to connect to the device and transfer files, choosing the `SFTP` protocol and entering the device and account information to connect.

## Packaging Applications

Using MaixPy + MaixVison makes it easy to develop, package, and install applications for easy offline deploy:
- Develop applications with MaixPy in MaixVision, which can be a single file or a project directory.
- Connect the device.
- Click the "Install" button at the bottom-left corner of MaixVision, fill in the basic information of the application in the popup window, where the ID is used to identify the application. A device cannot simultaneously install different applications with the same ID, so the ID should be different from the IDs of applications on MaixHub. The application name can be duplicated. You can also upload an icon.
- Click "Package Application" to package the application into an installer. If you want to upload it to the [MaixHub App Store](https://maixhub./com/app), you can use this packaged file.
- Click "Install Application" to install the packaged application on the device.
- Disconnect from the device, and you will see your application in the device's app selection interface. Simply click on it to run the application.

> If you develop with MaixCDK, you can use `maixcdk release` to package an application. Refer to the MaixCDK documentation for specifics.

## Using Graphical Block Programming

Under development, please stay tuned.

