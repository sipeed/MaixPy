---
title: 添加额外的 Python 软件包
---

## 简介

MaixPy 基于 Python 语言，提供了大量方便嵌入式应用开发的功能和 API，除此之外，你也可以使用其它的 Python 包来扩展功能。



## 安装额外的 Python 包

> 注意可能不是所有 Python 包都支持，一般只支持纯 Python 包，不支持 C 扩展包， C 扩展包可能需要你手动在电脑交叉编译（比较复杂，这里就不介绍了）。

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





