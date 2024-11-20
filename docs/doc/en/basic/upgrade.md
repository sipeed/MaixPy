---
title: MaixCAM MaixPy Upgrade and System Flashing
---

## Introduction to the System and MaixPy

First, let's distinguish between **`System`** and **`MaixPy`**:
* **System**: The foundation for running all software, including the operating system and drivers, serving as the cornerstone for software operation.
* **MaixPy**: A software package that relies on system drivers to function.

---

## Obtaining the Latest System

Visit the [MaixPy Release Page](https://github.com/sipeed/MaixPy/releases) to find the latest system image file, such as `maixcam_os_20240401_maixpy_v4.1.0.xz`.
> **Note for users in China:** Download speeds may be slow. Consider using Xunlei for potentially faster downloads.  
> Alternatively, use proxy websites like [github.abskoop.workers.dev](https://github.abskoop.workers.dev/) for downloading.  

Backup download link: [Sourceforge](https://sourceforge.net/projects/maixpy/files/) (May not always be up-to-date; prioritize the methods above.)

---

## Backing Up Data

**Updating (flashing) the system will erase all data.**
If you have important data stored on the system, back it up to your computer before proceeding.

### Backup Methods:
1. Connect MaixVision and use its file management feature to download your important files to your local computer.
2. Use the `scp` command to copy files.
3. Transfer files using other file management software, such as WinSCP or FileZilla.
4. Insert the TF card directly into a card reader and copy the data.
   Note: The root directory uses the `ext4` format, which is not natively supported by Windows. You can use third-party software like DiskGenius to access the data.

---

## Flashing the System onto MaixCAM

Refer to the hardware documentation's [MaixCAM System Flashing Guide](https://wiki.sipeed.com/hardware/zh/maixcam/os.html).  
If the conditions for **USB flashing** are met, it is recommended to use this method, as it avoids removing the TF card.

---

## When to Update the System vs. Updating MaixPy Only

To simplify the process and avoid issues, it is **recommended to update the system whenever upgrading MaixPy**.

### You **must** update the system in any of the following scenarios:
1. Using a new TF card, which requires a TF card reader for system flashing.
2. Upgrading MaixPy, and the [MaixPy Release Page](https://github.com/sipeed/MaixPy/releases) indicates that any version between the current and target versions includes a system update.
   > For example, if your current system is `maixcam_os_20240401_maixpy_v4.1.0` and you wish to upgrade to `4.7.8`, you must update the system if any version between `4.1.0` and `4.7.8` includes a system update. Failure to do so may result in MaixPy not functioning properly.

### It is **strongly recommended** to update the system in these cases:
1. When using the device for the first time, as the factory-installed system version may be outdated. Upgrade to the latest version to ensure compatibility with the documentation.

### Avoid updating in the following cases:
1. The current version meets your requirements and is running stably in critical scenarios (e.g., during competitions or product deployment).
2. The update introduces new features, but as a development kit, it may cause minor code incompatibilities or introduce bugs. Only update if you are prepared for development and debugging.

---

## Upgrading MaixPy Only

After carefully considering the points above, if you decide to upgrade MaixPy only, here are three methods:

1. Use the `ssh terminal` feature in MaixVision and run:
   ```
   pip install -U MaixPy
   ```
   For faster downloads in China, use:
   ```
   pip install -U MaixPy -i https://pypi.mirrors.ustc.edu.cn/simple
   ```

2. In MaixVision, execute the `examples/tools/install_maixpy.py` script to upgrade.

3. Manually download the file [MaixPy-x.x.x-py3-none-any.whl](https://github.com/sipeed/MaixPy/releases), transfer it to the device, and install it using either of the following methods:
   - Run `pip install xxx.whl` in the `ssh terminal`.
   - Execute:
     ```python
     import os
     os.system("xxx.whl")
     ```

**Note**: The process may take a while. Please be patient.
