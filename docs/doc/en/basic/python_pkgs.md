---
title: MaixCAM MaixPy Add extra Python packages.
---

## Introduction

MaixPy is based on the Python language and provides a wide range of functionalities and APIs for embedded application development. In addition to this, you can also use other Python packages to extend its functionality.

## Installing Additional Python Packages

> Please note that not all Python packages are supported. Generally, only pure Python packages are supported, not C extension packages. C extension packages may require you to manually cross-compile them on a computer (which is quite complex and won't be covered here).

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
