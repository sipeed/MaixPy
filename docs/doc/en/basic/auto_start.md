---
title: MaixPy/MaixCAM Application Auto-Start at Boot
---

Packaged applications can be set to automatically start when the device boots up, bypassing the application menu and directly launching the specified application.

## Method One for Setting Application Auto-Start

First, package and install the application, then go to `Settings -> Auto-Start` on your device to select the application you want to auto-start. To cancel auto-start, you can also adjust it here.

## Method Two for Setting Application Auto-Start

You can also modify the `/maixapp/auto_start.txt` file in your device to set it up. For methods on file transfer, refer to the previous documentation.
* First, determine the `id` of the application you want to set. This is set when you package the application; if it's not an application you packaged yourself, you can install it on the device and check the folder names under the device's `/maixapp/apps/` directory, which are the application names (or you can download and check the device's `/maixapp/apps/app.info` file, where the application `id` is indicated inside the `[]` brackets).
* Then write the `id` into the `/maixapp/auto_start.txt` file. (You can create the file locally on your computer, and then transfer it to the device using `MaixVision`.)
* To cancel, delete the `/maixapp/auto_start.txt` file on the device.

## Other Methods

For MaixCAM, since the underlying system is Linux, if you are familiar with Linux, you can edit the startup scripts in `/etc/rc.local` or `/etc/init.d`.

However, it is important to note that this method may cause the application to continue running when MaixVision connects, thereby occupying resources (such as the screen and camera) which might prevent MaixVision from running programs normally. The first two methods allow MaixVision to terminate the program upon connection to run its own programs.

Thus, this method is more suitable for running background processes that do not occupy screen and camera resources. Generally, if you are not familiar with Linux, it is not recommended to use this method.

