---
title: MaixCAM MaixPy Application Development and App Store
---

## Where to Find Applications

After booting, the device will automatically enter the application selection interface. Pre-installed apps are published in the [MaixHub App Store](https://maixhub.com/app), where you can find descriptions and usage instructions for each app.

## Where to Find Source Code

If available, source code links can be found on each application's page in the app store.

All official integrated application source codes are located in the [MaixPy/projects](https://github.com/sipeed/MaixPy/tree/main/projects) or [MaixCDK/projects](https://github.com/sipeed/MaixCDK/tree/main/projects) directories.

## How to Install Applications

There are several methods:

### Online QR Code Installation

You can first set the language via `Settings -> Language` and Wi-Fi via `Settings -> WiFi`.

Once connected to a Wi-Fi network with internet access, you can scan a QR code in the [MaixHub App Store](https://maixhub.com/app) to install apps.

### Local Installation

Upload the app package to the device and install it using the command:

```shell
app_store_cli install <path_to_package>
```

Alternatively, use the script [MaixPy/examples/tools/install\_app.py](https://github.com/sipeed/MaixPy). Be sure to modify the `pkg_path` variable to your package path.

### Local QR Code Installation for Local Package

* You can start a local service on your PC using:

```shell
maixtool deploy --pkg <path_to_package>
```

Then scan the QR code in the `App Store` app on your device to install the local package.

> Ensure `maixtool` is installed on your PC via `pip install maixtool`.

* If the app is developed using **MaixPy**, run `maixtool deploy` in the project root directory (containing `app.yaml` and `main.py`) to display a QR code. Keep the device and computer on the same LAN. The device can scan the QR code to install the app.
* If the app is developed using **MaixCDK**, run `maixcdk deploy` in the project root directory to generate a QR code for installation in the same manner.

## How to Uninstall Applications

On the device, open the `App Store` app and select `Uninstall App`.

Alternatively, use the script [MaixPy/examples/tools/uninstall\_app.py](https://github.com/sipeed/MaixPy) and set the `app_id` to the target application.

To list installed apps and get their IDs, run the script [MaixPy/examples/tools/list\_app.py](https://github.com/sipeed/MaixPy).

## App Ecosystem Overview

To enable out-of-box experience, reduce the entry barrier for users, and provide an efficient way for developers to share and even monetize their apps, we've created a simplified application framework including:

* **[App Store](https://maixhub.com/app)**: Developers can upload and share apps. Users can download and use them without coding. Developers can receive cash rewards (from MaixHub or user donations).
* **Pre-installed Applications**: Official apps include color tracking, AI object tracking, QR code scanning, face recognition, etc. They can be used directly or as serial communication modules.
* **MaixPy + MaixCDK SDKs**: Use [MaixPy](https://github.com/sipeed/maixpy) (Python) or [MaixCDK](https://github.com/sipeed/MaixCDK) (C/C++) to quickly build embedded AI vision/audio applications.
* **MaixVision PC Tool**: A user-friendly development tool for writing, debugging, deploying code, and installing apps. It even supports block-based programming for beginners and children.

Please explore the App Store, share your apps, and contribute to the community!

## How to Package Applications

* **Using MaixVision**: Refer to the [MaixVision documentation](./maixvision.md) for the app packaging section.
* **Manual Packaging**: In your project root directory, manually add an `app.yaml` file. Follow the [Maix APP Specification](https://wiki.sipeed.com/maixcdk/doc/zh/convention/app.html), then run `maixtool release` (for MaixPy) or `maixcdk release` (for MaixCDK) to package your app.

## How to Exit an Application

If your app doesn't have a UI or exit button, you can press the device's function key (usually labeled USER, FUNC, or OK) or a back button (if available — note that MaixCAM doesn't have a back button by default) to exit.

## Application Development Guidelines

* All MaixCAM devices come with a touchscreen, so it's recommended to create a simple UI with basic touch interaction. Refer to existing examples for implementation.
* Make UI elements and buttons large enough. MaixCAM has a 2.3" screen with 552x368 resolution — keep usability in mind for fingers.
* Each app should implement basic serial communication based on the [communication protocol](https://github.com/sipeed/MaixCDK/blob/master/docs/doc/convention/protocol.md) ([example](https://github.com/sipeed/MaixPy/tree/main/examples/communication/protocol)). For example, a face detection app can output coordinates via serial when a face is detected.

## Enable App Auto-Start on Boot

Refer to [Auto Start Application](./auto_start.md)

## System Configuration

Some system settings (e.g., language, backlight) can be accessed in the Settings app. Use `maix.app.get_sys_config_kv(item, key)` to fetch these values:

```python
from maix import app
locale = app.get_sys_config_kv("language", "locale")
print("locale:", locale)

backlight = app.get_sys_config_kv("backlight", "value")
print("backlight:", backlight, ", type:", type(backlight))
```

**Note**: All setting values are **strings**, so cast them appropriately when used.

Configuration is stored in the `/boot/configs` file. You may edit it offline, but ensure correct formatting.

The format is `maix_<item>_<key>=value`, and must be shell-compatible (no spaces around `=`).

Example (partial) content of `/boot/configs`:

```ini
# All configs user can edit easily
# Format: maix_<item>_<key>=value
#         all key characters should be lowercase
# Full supported items see documentation of maixpy at:
#      https://wiki.sipeed.com/maixpy/doc/zh/basic/app.html

### [language]
maix_language_locale=en

### [wifi]
# can be "ap" or "sta" or "off"
maix_wifi_mode=sta
maix_wifi_ssid=Sipeed_Guest
maix_wifi_passwd=qwert123
# encryption, auto detected by default. Can be:
# "NONE", "WPA-PSK", "WPA-EAP", "SAE"
# maix_wifi_encrypt="WPA-PSK"

### [comm] Maix comm protocol
# can be "uart" or "none"
maix_comm_method=uart

## [backlight] Screen backlight, from 0 to 100
maix_backlight_value = 50

### [npu]
# for MaixCAM2, enable AI ISP(1) or not(0)
# AI ISP improves image quality but occupies half NPU
maix_npu_ai_isp=0
```
