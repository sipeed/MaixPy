---
title: App development and app stores
---

## Introduction to Application Ecosystem

In order to make the development board ready to use out of the box, make it easy for users to use without barriers, enable developers to share their interesting applications, and provide effective channels for receiving feedback and even profits, we have launched a simple application framework, including:

- **[App Store](https://maixhub.com/app)**: Developers can upload and share applications, which users can download and use without needing to develop them. Developers can receive certain cash rewards (from MaixHub or user tips).
- **Pre-installed Apps**: The official provides some commonly used applications, such as color block detection, AI object detection tracking, QR code scanning, face recognition, etc., which users can use directly or use as serial module.
- **MaixPy + MaixCDK Software Development Kit**: Using [MaixPy](https://github.com/sipeed/maixpy) or [MaixCDK](https://github.com/sipeed/MaixCDK), you can quickly develop embedded AI visual and audio applications in Python or C/C++, efficiently realizing your interesting ideas.
- **MaixVision Desktop Development Tool**: A brand-new desktop code development tool for quick start, debugging, running, uploading code, installing applications to devices, one-click development, and even support for graphical block-based programming, making it easy for elementary school students to get started.

Everyone is welcome to pay attention to the App Store and share their applications in the store to build a vibrant community together.


## Packaging Applications

Using MaixPy + MaixVison makes it easy to develop, package, and install applications:
- Develop applications with MaixPy in MaixVision, which can be a single file or a project directory.
- Connect the device.
- Click the "Install" button at the bottom-left corner of MaixVision, fill in the basic information of the application in the popup window, where the ID is used to identify the application. A device cannot simultaneously install different applications with the same ID, so the ID should be different from the IDs of applications on MaixHub. The application name can be duplicated. You can also upload an icon.
- Click "Package Application" to package the application into an installer. If you want to upload it to the [MaixHub App Store](https://maixhub./com/app), you can use this packaged file.
- Click "Install Application" to install the packaged application on the device.
- Disconnect from the device, and you will see your application in the device's app selection interface. Simply click on it to run the application.

> If you develop with MaixCDK, you can use `maixcdk release` to package an application. Refer to the MaixCDK documentation for specifics.

## Exiting Applications

If you have developed a relatively simple application without a user interface and a back button, you can exit the application by pressing the device's function button (usually labeled as USER, FUNC, or OK) or the back button (if available, MaixCAM does not have this button by default).


## Basic Guidelines for Application Development

- Since touchscreens are standard, it is recommended to create a simple interface with touch interaction. You can refer to examples for implementation methods.
- Avoid making interfaces and buttons too small, as MaixCAM default screen is 2.3 inches with 552x368 resolution and high PPI. Make sure fingers can easily tap without making mistakes.
- Implement a simple serial interaction for the main functionality of each application based on the [serial protocol](https://github.com/sipeed/MaixCDK/blob/master/docs/doc/convention/protocol.md) (see [example](https://github.com/sipeed/MaixPy/tree/main/examples/communication/protocol)). This way, users can directly use it as a serial module. For instance, in a face detection application, you can output coordinates via serial port when a face is detected.
