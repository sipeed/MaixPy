---
title: Burning system
---

## Introduction to the System and MaixPy

First, let's distinguish between **`System`** and **`MaixPy`**:
* **System**: The foundation for running all software, including the operating system and drivers, serving as the cornerstone for software operation.
* **MaixPy**: A software package that relies on system drivers to function.

## Get the Latest System and Flash It to Hardware

Before flashing, confirm both the device model and where the system is stored. MaixCAM / MaixCAM-Pro run the system from a TF card, so a TF card is required. MaixCAM2 normally runs from onboard eMMC, so a TF card is usually not required for regular updates. For regular updates, use the USB flashing workflow in the corresponding flashing page first; when booting from a TF card, recovering the system, or replacing storage media, follow the method described on that page.

After confirmation, use the table below to choose the correct system image and flashing page.

| Device | Download entry | File to choose | Flashing page |
| --- | --- | --- | --- |
| MaixCAM | [GitHub download](https://github.com/sipeed/MaixPy/releases) | `maixcam-*.img.xz` | [MaixCAM System Flashing](https://wiki.sipeed.com/hardware/zh/maixcam/os.html) |
| MaixCAM-Pro | [GitHub download](https://github.com/sipeed/MaixPy/releases) | `maixcam-pro-*.img.xz` | [MaixCAM System Flashing](https://wiki.sipeed.com/hardware/zh/maixcam/os.html) |
| MaixCAM2 | [Baidu Netdisk (extraction code: dshn)](https://pan.baidu.com/s/1nk60bNu5QhdNAsp7e_c-xw) | `maixcam2-*-maixpy-*_sd.img.7z.*` | [MaixCAM2 System Flashing](https://wiki.sipeed.com/hardware/zh/maixcam/maixcam2_os.html) |

> For users in mainland China, if GitHub access is slow, the matching system image can also be downloaded from the MaixPy (v4) AI Vision official QQ group files (QQ group: 862340358).

<span style="color: #e91e63; font-weight: 800">**Make sure to download the system image that corresponds to your device model**</span>. Downloading the wrong image may cause abnormal behavior and may require recovery flashing.

When downloading, choose the newest file that matches the "File to choose" column in the table. For MaixCAM and MaixCAM-Pro, select the corresponding image from the GitHub download page. MaixCAM2 images are split 7z archives; download all `.7z.00x` parts of the same version from Baidu Netdisk before extracting and flashing.

## Backup Your Data

**Updating (flashing) the system will erase all data.**
If you have important data saved on the device, please back it up to your computer first.

Choose a backup method in the following order. After backing up, open the backup folder on your computer and confirm that the files are present before flashing.

1. **Recommended: back up with the MaixVision file manager**. Connect the device to your computer over USB, connect it in MaixVision, open the device file manager, then enter `/maixapp` and `/root` and download the projects, models, images, and configuration files you need to keep to a local folder on your computer.
2. **Advanced: back up with the `scp` command**. If you are already familiar with terminals and SSH, run the following commands on your computer. Replace `<device_ip_or_name>` with the device IP address or device name, which can be found in "Settings -> Device Information" on the device. The default password is `root` for MaixCAM / MaixCAM-Pro and `sipeed` for MaixCAM2.

   ```bash
   mkdir maix_backup
   scp -r root@<device_ip_or_name>:/maixapp ./maix_backup/
   scp -r root@<device_ip_or_name>:/root ./maix_backup/
   ```

   If you are not familiar with SSH or `scp`, read the connection instructions in [Linux basics](./linux_basic.md) first.
3. **Alternative: back up with WinSCP / FileZilla**. This is suitable if you do not want to use the command line. Install and open `WinSCP` or `FileZilla` on your computer, then enter the connection information: protocol `SFTP`, host as the device IP address or device name, port `22`, username `root`, and the password for your device model (`root` for MaixCAM / MaixCAM-Pro, `sipeed` for MaixCAM2). After connecting, the left side is the computer directory and the right side is the device directory. Open `/maixapp` and `/root` on the device side, then drag the files you need to keep to a backup folder on your computer.
4. **Alternative: back up with a TF card reader**. Power off the device, remove the TF card in use, insert it into your computer with a card reader, and copy the files you need to keep. If you need to read the Linux root partition, Windows cannot read `ext4` by default; use a Linux computer or a tool such as DiskGenius that supports `ext4`.


## When to Update the System

Updating the system rewrites the system image and is intended for issues related to the base system, drivers, system libraries, or boot process. Update the system first in any of the following cases:

1. The device cannot boot normally, system files are damaged, or the system storage medium has been replaced or formatted and needs a fresh system image.
2. You are using the device for the first time. The factory-installed system may be outdated, so update to the latest system first, then follow the current documentation for learning and development.
3. You are preparing a TF card for MaixCAM / MaixCAM-Pro for the first time. Open the corresponding flashing page from the table above and flash the latest system image once.
4. You want to upgrade MaixPy, and any release between the current version and the target version on the [GitHub download page](https://github.com/sipeed/MaixPy/releases) includes a system image update. Check the current system or MaixPy version in Settings -> Device Information on the device, then compare it with the target version and intermediate release notes on GitHub. If you cannot determine whether a system update is required, update the system directly.
5. The new feature you need explicitly depends on a newer system, driver, or system library, such as when the documentation, examples, or release notes require a system update first.

> For example, if your current system is `maixcam_os_20240401_maixpy_v4.1.0` and you want to upgrade to `4.7.8`, update the system if any version between `4.1.0` and `4.7.8` includes a system update. Otherwise, MaixPy or related features may not work properly.

If the current version already meets your requirements and the device is running stably in an important scenario such as a competition, demo, or product deployment, you can postpone the upgrade. When an upgrade is needed, back up your data first, then follow the flashing page for your device model.

## When MaixPy Can Be Updated Only

Updating MaixPy only does not reflash the system. It is suitable when the existing system environment already meets the requirements and only the Python package needs to be updated. Use this method only when all of the following conditions are met:

1. The device boots normally, and basic functions such as the camera, display, network, and file read/write are working.
2. You only need Python API updates, example updates, or bug fixes in MaixPy, and the update does not involve the system image, drivers, or low-level libraries.
3. You have checked the target version and intermediate release notes on the [GitHub download page](https://github.com/sipeed/MaixPy/releases), and confirmed that no required system update is mentioned.
4. You have backed up your data as described above. If compatibility issues occur after updating MaixPy only, return to the system update workflow and reflash the system.

If you are not sure whether these conditions are met, update the system directly. This is more reliable for beginners.

## How to Upgrade MaixPy Only

After confirming that MaixPy can be updated independently, choose one of the following methods. Beginners should use method 1 first. If the upgrade fails or you are not sure whether the system version matches, return to the section above and update the whole system.

1. **Upgrade online from the MaixVision terminal**: connect the device, open **Device Terminal / ssh terminal** in MaixVision, and run:

   ```bash
   pip install -U MaixPy
   ```

   For faster downloads in China, use:

   ```bash
   pip install -U MaixPy -i https://pypi.mirrors.ustc.edu.cn/simple
   ```

   When the command finishes without errors, restart the application or reboot the device, then run your program again to confirm that the version has been updated.
2. **Run the MaixVision example script**: in MaixVision examples, find `examples/tools/install_maixpy.py`, connect the device, and click Run. The script downloads and installs MaixPy automatically. After it finishes, restart the application or reboot the device as prompted.
3. **Manually install a `.whl` file**: download `MaixPy-x.x.x-py3-none-any.whl` from the [GitHub download page](https://github.com/sipeed/MaixPy/releases), upload it to `/root` on the device with the MaixVision file manager, then run the following command in the MaixVision terminal:

   ```bash
   pip install /root/MaixPy-x.x.x-py3-none-any.whl
   ```

   Replace the file name in the command with the actual file name you downloaded. Restart the application or reboot the device after installation.

**Note**: The process may take a while. Please be patient.
