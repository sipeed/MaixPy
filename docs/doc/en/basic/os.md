---
title: Upgrade and burn system.
---

## Introduction

If you have purchased the official (Sipeed) package with a TF card, typically the system has already been pre-programmed at the factory and can be used directly without further steps.

However, to avoid using an outdated version of the pre-programmed system, it is highly recommended to first upgrade to the latest system following the tutorial.

## How to Confirm if System Upgrade is Needed

* Upon booting up to the main menu, click on `Settings`, then `Device Info` to check the system's version number.
* Visit the [MaixPy Release History page](https://github.com/sipeed/MaixPy/releases) to review the update logs, which contain information on MaixPy firmware and system image updates. If there are significant updates after your current version, it is advisable to upgrade.
  
  > If the latest system update only includes routine MaixPy firmware updates compared to your current system, you may choose not to upgrade. You can simply update `MaixPy` separately in `Settings` under `Update MaixPy`.

## Obtaining the Latest System

Visit the [MaixPy Release page](https://github.com/sipeed/MaixPy/releases) to find the latest system image file, such as `maixcam_os_20240401_maixpy_v4.1.0.xz`.

Alternate link:
* [Sourceforge](https://sourceforge.net/projects/maixpy/files/)

## Burning the System Image to MaixCAM

Refer to the [MaixCAM System Burning](https://wiki.sipeed.com/hardware/zh/maixcam/os.html) tutorial. Note that if the conditions for `USB Burning` are met, it is recommended to use the `USB Burning` method. The USB burning method does not require removing the TF card.

