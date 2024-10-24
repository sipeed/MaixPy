---
title: MaixCAM 更新 MaixPy
---

有两种方法，如果第一次上手使用，为了降低难度，可以直接使用出厂 TF 卡自带的 MaixPy 固件尝试，以后再考虑更新。

不过因为不知道你拿到手的是什么时候出厂的 TF 卡，所以建议都更新一下系统。

## 直接更新系统（强烈推荐）

按照 [升级和烧录系统](./os.md) 中的操作升级到最新的系统，里面就包含了最新的 MaixPy 固件。


## 只更新 MaixPy 固件

在 [MaixPy 仓库 release 页面](https://github.com/sipeed/MaixPy/releases) 看到最新的版本信息和更新日志，其中包含了 MaixPy 固件信息，以及对应版本使用的系统信息。

如果不想更新系统（因为一般系统变动不大，可以看 MaixPy 更新日志中是否有系统改动相关，再决定是否更新系统），则可以只更新 MaixPy 固件。

* 在设置中设置 WiFi， 让系统联网。
* 点击设置应用中的 `更新 MaixPy` 进行更新。

也可以执行 Python 代码调用系统命令来更新：
```python
import os

os.system("pip install MaixPy -U")
```

由于默认从`pypi.org`下载，中国国内速度可能比较慢，可以设置国内的镜像站点，修改下面代码的 `server` 变量来选择，此脚本在`MaixPy` 的 `examples/tools` 目录下也有，可以直接在`MaixVision`中运行。

```python
import os

def install_maixpy(server):
    cmd = f"pip install maixpy -U -i {server}"
    print("Start install now, wait patiently ...")
    err = os.system(cmd)
    if err != 0:
        print("[ERROR] execute failed, code:", err)
    else:
        print("Install complete")


servers = {
    "pypi": "https://pypi.org/simple",
    "aliyun": "https://mirrors.aliyun.com/pypi/simple",
    "ustc": "https://pypi.mirrors.ustc.edu.cn/simple",
    "163": "https://mirrors.163.com/pypi/simple",
    "douban": "https://pypi.douban.com/simple",
    "tuna": "https://pypi.tuna.tsinghua.edu.cn/simple"
}

# Select server based on your network
server = servers["tuna"]

install_maixpy(server)
```

> 如果你会使用终端， 也可以直接在终端中使用 `pip install MaixPy -U` 来更新 MaixPy。

另外你也可以手动下载`wheel` 文件（`.whl`格式）传输到设备（传输方法见后文[MaixVision 使用](./maixvision.md)）后通过 `pip install ******.whl` 命令来安装。

