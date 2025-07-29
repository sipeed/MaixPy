---
title: Compiling a System for MaixCAM MaixPy
---

## Why Customize the System?

Typically, you can download the latest system for MaixCAM directly from [this link](https://github.com/sipeed/MaixPy/releases). However, there are some scenarios where you might need to customize the system:

* For example, if you are mass-producing 1,000 products and want each to have your own application that automatically starts on boot, without configuring each one individually, you can modify the `builtin_files` and package a system. Once this system is flashed onto the boards, they will all include your custom files, eliminating the need to copy them again after booting.
* If the official system does not include the software packages or drivers you need, you can compile your own system and select the packages you want to include.

## Obtaining the Base System

The principle is to use a system from [this link](https://github.com/sipeed/LicheeRV-Nano-Build/releases) as the base (note that this system cannot be directly flashed onto MaixCAM as it may damage the screen), then copy the MaixCAM-specific files into the base system and repackage it into a system usable by MaixCAM.

If you don't need to customize the base system, you can directly download the latest system image from [here](https://github.com/sipeed/LicheeRV-Nano-Build/releases).

If the base system doesn't meet your requirements, such as needing to add or remove some software packages and drivers, follow the instructions in the [LicheeRV-Nano-Build repository](https://github.com/sipeed/LicheeRV-Nano-Build) README to compile the system. It's recommended to use Docker for compilation to avoid environment issues and to use `bash` instead of `zsh`.

Remember, the compiled system should not be flashed directly onto MaixCAM, as it might damage the screen.

## Copying Files for MaixCAM

Prepare the following:

* The base system, which is a `.img` or `.img.xz` file.
* Additional files for MaixCAM can be downloaded from the [MaixPy release page](https://github.com/sipeed/MaixPy/releases). Download the latest `builtin_files.tar.xz`.
> If you need to add custom files to the system, you can extract the files and add them to the appropriate directory. For example, if you want a `cat.jpg` file to be in the `/root` directory after flashing, simply place `cat.jpg` in the `root` directory.
* Download or clone the MaixPy source code locally.
* Compile MaixPy to obtain the `.whl` installation package, or you can download the latest installation package from the [MaixPy release page](https://github.com/sipeed/MaixPy/releases).

In the `MaixPy/tools/os` directory, run the following command:

```shell
./gen_os.sh <base_os_filepath> <maixpy_whl_filepath> <builtin_files_dir_path> [skip_build_apps] [device_name]
```

Here’s what each parameter means:
* **base_os_filepath**: The path to the base system, in `.img` or `.img.xz` format.
* **maixpy_whl_filepath**: The MaixPy package, in `.whl` format.
* **builtin_files_dir_path**: The custom files for MaixCAM, which can be downloaded from the MaixPy release page.
* **skip_build_apps**: Skip compiling built-in applications, optional arg. Set to 1 to skip, no this arg it will compile and copy apps from MaixCDK and MaixPy into the system.
* **device name**: Can be `maixcam` or `maixcam-pro`

Example command:

```shell
./gen_os.sh '/home/xxx/.../LicheeRV-Nano-Build/install/soc_sg2002_licheervnano_sd/images/2024-08-13-14-43-0de38f.img' ../../dist/MaixPy-4.4.21-py3-none-any.whl '/home/xxx/.../maixcam_builtin_files' 0 maixcam-pro
```

After waiting for the built-in apps to compile and copy, you should find a `maixcam-pro-2024-08-15-maixpy-v4.4.21.img.xz` system image in the `MaixPy/tools/os/tmp` directory.
