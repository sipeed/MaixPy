---
title: MaixVision - MaixPy Programming + Graphical Block Programming
---

## Introduction

[MaixVision](https://wiki.sipeed.com/maixvision) is a developer programming tool specifically designed for the Maix ecosystem, supporting MaixPy programming and graphical block programming. It also supports online running, debugging, and real-time image preview, allowing the synchronization of the device display screen for easy debugging and development.

It also supports packaging applications and installing them on devices, making it convenient for users to generate and install applications with a single click.

Additionally, it integrates some handy development tools, such as file management, threshold editors, QR code generators, and more.

## Download

Visit [MaixVision home page](https://wiki.sipeed.com/maixvision) to download.

## Using MaixPy Programming and Online Running

By following the steps in the [Quick Start](../README.md), we can easily use MaixPy programming and run programs online.

## Real-time Image Preview

MaixPy provides a `display` module, which can display images on the screen. When calling the `show` method of the `display` module, the image will be sent to MaixVision for display in real-time, for example:

```python
from maix import display, camera

cam = camera.Camera(640, 480)
disp = display.Display()
while 1:
    disp.show(cam.read())
```

Here, we capture an image using the camera, and then display it on the screen using `disp.show()`, which will also transmit the image to MaixVision for display.

By clicking the `Pause` button in the top right corner, the transmission of the image to MaixVision display will stop.

## Computing the Histogram of an Image

In the previous step, we could see the image in real-time on MaixVision. By selecting a region with the mouse, we can view the histogram of that area below the image. Choosing different color representation methods allows us to see histograms of different color channels. This feature helps us find suitable parameters when working on image processing algorithms.

## Using Graphical Block Programming

Currently in development, stay tuned for updates.

## Distinguishing Between `Device File System` and `Computer File System`

An important concept to grasp here is distinguishing between the **`Computer File System`** and **`Device File System`**:

- **Computer File System**: This operates on the computer. Opening files or projects in MaixVision accesses files stored on the computer. Any changes are automatically saved to the computer's file system.
- **Device File System**: When a program runs, it sends files to the device for execution. Therefore, files accessed within the code are read from the device's file system.

A common issue arises when a file is saved on the computer at `D:\data\a.jpg`, and then the file is referenced on the device like `img = image.load("D:\data\a.jpg")`. This file cannot be found on the device because there is no `D:\data\a.jpg` file stored there.

For specific instructions on transferring computer files to the device, please refer to the following section.

## Transferring Files to the Device

Currently in development. In the meantime, you can use alternative tools:

Begin by knowing the device's IP address or device name, which MaixVision can search for, or check in the device's `Settings -> System Information`, where you might find something similar to `maixcam-xxxx.local` or `192.168.0.123`. The username and password are both `root`, and the file transfer protocol is `SFTP` with port number `22`.

There are various user-friendly software options available for different operating systems:

### For Windows

Use tools like [WinSCP](https://winscp.net/eng/index.php) or [FileZilla](https://filezilla-project.org/) to connect to the device via `SFTP`. Provide the necessary device and account information to establish the connection.

For further guidance, perform a quick online search.

### For Linux

Use the `scp` command in the terminal to transfer files to the device, for example:

```bash
scp /path/to/your/file.py root@maixcam-xxxx.local:/root
```

### For Mac

- **Method 1**: Use the `scp` command in the terminal to transfer files to the device, for example:

```bash
scp /path/to/your/file.py root@maixcam-xxxx.local:/root
```

* **Method 2**: Use tools like [FileZilla](https://filezilla-project.org/) to connect to the device, transfer the files to the device, choose the `SFTP` protocol, fill in the device and account information, and connect.



## Code Completion

Code completion depends on the Python packages installed locally on your computer. To enable code completion, you need to install Python on your computer and also the Python packages required for completion.

* To install Python, visit the [Python official website](https://python.org/) for installation.
* To install the packages required for completion, for instance, for MaixPy, you need to install the MaixPy package on your computer as well by using `pip install MaixPy`.
* Restart MaixVision to see the code completion.

> If the completion still does not work, you can manually set the path to the python executable in the settings and restart.

>! Note that installing Python packages on your computer is only for code completion purposes. The actual code still runs on the device (development board), and the device must also have the corresponding packages for proper operation.

> Additionally, although you have installed the MaixPy package on your computer, due to our limited resources, we do not guarantee that you will be able to directly import the maix package in Python on your computer for use. Please run it on supported devices.

