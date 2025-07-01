---
title: MaixCAM MaixPy Add extra Python packages.
---

## Introduction

MaixPy is based on the Python language and provides a wide range of functionalities and APIs for embedded application development. In addition to this, you can also use other Python packages to extend its functionality.

## Installing Additional Python Packages

> Note: Since MaixCAM uses a custom RISC-V toolchain, **not all Python packages are supported**. Generally, only **pure Python packages** are supported — C extension packages are **not supported** unless you manually cross-compile them on your PC (which is more complex and not covered here).

> For **MaixCAM2**, which is **AARCH64** and comes with a built-in **GCC**, you can assume that **almost all Python packages can be installed**.


### Method 1: Installing Using Python Code

You can install the package you need in MaixVision using Python code, for example:

```python
import os
os.system("pip install package_name")
```

To update a package, you can use:

```python
import os
os.system("pip install --upgrade package_name")
```

### Method 2: Installing Using the Terminal and pip Command

Follow the terminal usage method introduced in [Linux Basics](./linux_basic.md) and use `pip install package_name` to install the package you need.


## Packages That Cannot Be Installed Directly with pip

> This issue mainly affects MaixCAM/MaixCAM-Pro. MaixCAM2 generally does not have this problem.


pip on the device can install programs written in pure Python. However, for libraries that use other languages like C++ at the lower level, there are generally no precompiled packages available due to the unique nature of MaixCAM RISC-V.

Solutions:
* **Method 1:** Find the source code of the corresponding package, cross-compile it into a `.whl` installation package on your computer, and then copy it to the device and use `pip install xxxx.whl` to install it. The toolchain used for compilation is the same as the one used by [MaixCDK](https://github.com/sipeed/MaixCDK/blob/main/platforms/maixcam.yaml).
* **Method 2:** According to the [compilation system](../pro/compile_os.md), before compiling, you can execute `make menuconfig` in the `buildroot` directory to check if the Python interpreter's extra packages contain the software you need. After selecting it, you can recompile the system image to include the package.
> If you successfully compile and test a package using Method 2 and find it necessary to integrate into the system, feel free to provide feedback through [issues](https://github.com/sipeed/maixpy/issues).

