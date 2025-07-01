---
title: MaixCAM MaixPy 添加额外的 Python 软件包
---

## 简介

MaixPy 基于 Python 语言，提供了大量方便嵌入式应用开发的功能和 API，除此之外，你也可以使用其它的 Python 包来扩展功能。



## 安装额外的 Python 包

> 注意由于 MaixCAM 是 RISC-V 而且定制工具链， 可能不是所有 Python 包都支持，一般只支持纯 Python 包，不支持 C 扩展包， C 扩展包可能需要你手动在电脑交叉编译（比较复杂，这里就不介绍了）。
> 对于 MaixCAM2，是 AARCH64, 而且内置了 GCC，所以可以认为能安装所有包。

### 方法一： 使用 Python 代码来安装

在 MaixVision 中使用 Python 代码来安装你需要的包，比如：

```python
import os
os.system("pip install 包名")
```

要更新一个包，可以使用：

```python
import os
os.system("pip install --upgrade 包名")
```

### 方法二： 终端使用 pip 命令安装

使用[Linux 基础](./linux_basic.md)中介绍的终端使用方法，使用 `pip install 包名` 安装你需要的包。

## pip换源

在使用 pip 下载 Python 软件包时，默认会从 [PyPI](https://pypi.org/) 下载。PyPI 是 Python 官方的软件包储存库，对于中国用户来说下载速度会很慢。

中国国内有许多 PyPI 的镜像源，从镜像源下载可以提升下载速度。

在终端中输入以下命令，可以从清华源更新 pip ：

```
python -m pip install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple --upgrade pip
```

用以下命令将下载源设为清华源：

```
pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
```

恢复默认源：

```
pip config unset global.index-url
```

参考：[清华大学开源软件镜像站 PyPI软件仓库](https://mirrors.tuna.tsinghua.edu.cn/help/pypi/)。

你也可以自己寻找其他好用的镜像源。

## pip 无法直接安装的包

主要是 MaixCAM/MaixCAM-Pro 会有这个问题，MaixCAM2 一般不存在这个问题。

设备内 pip 能安装纯 Python 编写的程序，对于底层使用了其它语言比如 C++ 编写的库由于 MaixCAM RISC-V 的特殊性，一般没有直接可以用的编译好的包。

解决方法：
* 方法一： 找到对应的包源码，在电脑上交叉编译成 whl 安装包，然后复制到设备里面使用`pip install xxxx.whl`安装。编译的工具链和[MaixCDK 使用的工具链相同](https://github.com/sipeed/MaixCDK/blob/main/platforms/maixcam.yaml)。
* 方法二： 根据[编译系统](../pro/compile_os.md)中描述编译系统，编译前可以到`buildroot`目录下执行`make menuconfig`找找 Python 解释器 额外包中有没有你想要的软件包，勾选上再编译就能将改包编译进系统镜像。
> 如果你通过方法二成功编译测试过了某个包并且觉得它十分有必要集成到系统中，欢迎通过[issues](https://github.com/sipeed/maixpy/issues) 提意见。


