---
title: MaixCAM MaixPy App development and app stores
---

## Where to Find Applications

After powering on, the device will automatically enter the application selection interface. All built-in applications are available on the [MaixHub App Store](https://maixhub.com/app), where you can find corresponding app descriptions and usage instructions.

## Where to Find Source Code

You can find the source code links (if available) on the app pages in the App Store. The source code for official integrated applications is located in the [MaixPy/projects](https://github.com/sipeed/MaixPy/tree/main/projects) directory or the [MaixCDK/projects](https://github.com/sipeed/MaixCDK/tree/main/projects) directory.

## Installing Applications

Frequently used settings include `Settings -> Language` and `Settings -> WiFi`.

The `App Store` application can be used to upgrade and install apps. Once connected to a WiFi network with internet access, you can scan to install apps from the [MaixHub App Store](https://maixhub.com/app).

## Uninstalling Applications

You can uninstall applications using the `Uninstall App` feature in the `App Store` application on the device.

You can also execute the script [MaixPy/examples/tools/uninstall_app.py](https://github.com/sipeed/MaixPy), setting the `app_id` variable to the ID of the application you want to uninstall. The `app_id` can be viewed by executing the `MaixPy/examples/tools/list_app.py` script to see the IDs of installed applications.

## Introduction to Application Ecosystem

In order to make the development board ready to use out of the box, make it easy for users to use without barriers, enable developers to share their interesting applications, and provide effective channels for receiving feedback and even profits, we have launched a simple application framework, including:

- **[App Store](https://maixhub.com/app)**: Developers can upload and share applications, which users can download and use without needing to develop them. Developers can receive certain cash rewards (from MaixHub or user tips).
- **Pre-installed Apps**: The official provides some commonly used applications, such as color block detection, AI object detection tracking, QR code scanning, face recognition, etc., which users can use directly or use as serial module.
- **MaixPy + MaixCDK Software Development Kit**: Using [MaixPy](https://github.com/sipeed/maixpy) or [MaixCDK](https://github.com/sipeed/MaixCDK), you can quickly develop embedded AI visual and audio applications in Python or C/C++, efficiently realizing your interesting ideas.
- **MaixVision Desktop Development Tool**: A brand-new desktop code development tool for quick start, debugging, running, uploading code, installing applications to devices, one-click development, and even support for graphical block-based programming, making it easy for elementary school students to get started.

Everyone is welcome to pay attention to the App Store and share their applications in the store to build a vibrant community together.


## Packaging Applications

See [MaixVision Usage](./maixvision.md) Packaging Applications part.

## Exiting Applications

If you have developed a relatively simple application without a user interface and a back button, you can exit the application by pressing the device's function button (usually labeled as USER, FUNC, or OK) or the back button (if available, MaixCAM does not have this button by default).

## Installing Applications

* **Method 1**: Use the `App Store` application on the device. Find the application on the [App Store](https://maixhub.com/app), connect the device to the internet, and scan the code to install.

* **Method 2**: Install using a local installation package. Transfer the package to the device's file system, for example, to `/root/my_app_v1.0.0.zip`, and then run the following code. Make sure to modify the `pkg_path` variable to the correct path, you can also find this script in `MaixPy`'s `examples/tools/install_app.py`:
```python
import os

def install_app(pkg_path):
    if not os.path.exists(pkg_path):
        raise Exception(f"Package {pkg_path} not found")
    cmd = f"/maixapp/apps/app_store/app_store install {pkg_path}"
    err_code = os.system(cmd)
    if err_code != 0:
        print("[ERROR] Install failed, error code:", err_code)
    else:
        print(f"Install {pkg_path} success")

pkg_path = "/root/my_app_v1.0.0.zip"

install_app(pkg_path)
```

* **Method 3**:
  * For applications developed using `MaixPy`, run `maixtool deploy` in the project root directory (which contains `app.yaml` and `main.py`). A QR code will be displayed. Keep the device and computer on the same local network, and use the App Store on the device to scan the QR code corresponding to the local network address for online installation.
  * For applications developed using `MaixCDK`, run `maixcdk deploy` in the project root directory. A QR code will be displayed. Keep the device and computer on the same local network, and use the App Store on the device to scan the QR code corresponding to the local network address for online installation.

## Basic Guidelines for Application Development

- Since touchscreens are standard, it is recommended to create a simple interface with touch interaction. You can refer to examples for implementation methods.
- Avoid making interfaces and buttons too small, as MaixCAM default screen is 2.3 inches with 552x368 resolution and high PPI. Make sure fingers can easily tap without making mistakes.
- Implement a simple serial interaction for the main functionality of each application based on the [serial protocol](https://github.com/sipeed/MaixCDK/blob/master/docs/doc/convention/protocol.md) (see [example](https://github.com/sipeed/MaixPy/tree/main/examples/communication/protocol)). This way, users can directly use it as a serial module. For instance, in a face detection application, you can output coordinates via serial port when a face is detected.

## APP power on auto start

Refer to [APP auto start on power up](./auto_start.md).


## System Settings

The **System Settings** application contains several configuration items, such as language, screen brightness, etc. We can retrieve the values of these settings using `maix.app.get_sys_config_kv(item, key)`.

For example, to get the language setting:

```python
from maix import app
locale = app.get_sys_config_kv("language", "locale")
print("locale:", locale)

backlight = app.get_sys_config_kv("backlight", "value")
print("backlight:", backlight, ", type:", type(backlight))
```

Note: All setting values are of **string type**, so please be mindful of this when using them.


```ini
# All configs user can edit easily
# Format: maix_<item>_<key>=value
#         all key charactors should be lowercase
# Full supported items see documentation of maixpy at:
#      https://wiki.sipeed.com/maixpy/doc/zh/basic/app.html

### [language]
maix_language_locale=en

### [wifi]
# can be "ap" or "sta" or "off"
maix_wifi_mode=sta
maix_wifi_ssid=Sipeed_Guest
maix_wifi_passwd=qwert123
# encrypt default auto detect, you can also set it manually:
#   can be "NONE", "WPA-PSK", "WPA-EAP", "SAE"
# maix_wifi_encrypt="WPA-PSK"

### [comm] Maix comm protocol
# can be "uart" or "none"
maix_comm_method=uart

## [backlight] Screeen backlight, from 0 to 100
maix_backlight_value = 50

### [npu]
# for maixcam2, enable AI ISP(1) or not(0),
# enalbe AI ISP will get better camera quality and occupy half of NPU.
maix_npu_ai_isp=0

```

