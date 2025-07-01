---
title: MaixCAM MaixPy Upgrade and System Flashing
---

## Introduction to the System and MaixPy

First, let's distinguish between **`System`** and **`MaixPy`**:
* **System**: The foundation for running all software, including the operating system and drivers, serving as the cornerstone for software operation.
* **MaixPy**: A software package that relies on system drivers to function.

## Getting the Latest System

Find the latest system image files on the [MaixPy Releases page](https://github.com/sipeed/MaixPy/releases), for example:

* `maixcam_os_20240401_maixpy_v4.1.0.xz`: MaixCAM system image including MaixPy v4.1.0.
* `maixcam-pro_os_20240401_maixpy_v4.1.0.xz`: MaixCAM Pro system image including MaixPy v4.1.0.
* `maixcam2_os_20250801_maixpy_v4.11.0.xz`: MaixCAM2 system image including MaixPy v4.11.0.

<span style="color: #e91e63; font-weight: 800">**Make sure to download the system image that corresponds to your device model**</span>. Downloading the wrong image may cause device damage.

> Users in China with slow download speeds can use tools like Xunlei for faster downloads.
> Alternatively, use proxy sites such as [github.abskoop.workers.dev](https://github.abskoop.workers.dev/) for downloads.

Backup mirror: [Sourceforge](https://sourceforge.net/projects/maixpy/files/) (may not be up-to-date, so prefer the above official sources)


## Backup Your Data

**Updating (flashing) the system will erase all data.**
If you have important data saved on the device, please back it up to your computer first.

Backup methods:

* Connect with MaixVision and use the file manager to download important files to your computer, especially files under `/maixapp` and `/root`.
* Use the `scp` command to copy files.
* Use file transfer tools such as WinSCP or FileZilla.
* Remove the storage media and use a card reader to copy files directly. Note: the root filesystem is formatted as `ext4`, which Windows does not support by default (you can use third-party software like DiskGenius to read it).


## Flashing the System to Hardware

| Item          | MaixCAM / MaixCAM-Pro    | MaixCAM2      |
| --------------- | ---------- | ------ |
| Flashing Docs      | [MaixCAM System Flashing](https://wiki.sipeed.com/hardware/zh/maixcam/os.html) | [MaixCAM2 System Flashing](https://wiki.sipeed.com/hardware/zh/maixcam/os_maixcam2.html) |
| System Storage     | TF Card    | Built-in EMMC (/TF Card)    |
| TF Card Required   | Yes   | No   |
| Flashing Method    | USB flashing or card reader flashing   | USB flashing or card reader flashing |
| Recommended Method | USB flashing   | USB flashing   |
| Recovery Flashing  | Card reader flashing     | USB flashing / card reader flashing    |


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
