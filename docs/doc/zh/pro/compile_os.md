---
title: 为 MaixCAM 编译系统
---

## 为什么需要定制系统

正常情况下你只需要从 [https://github.com/sipeed/MaixPy/releases](https://github.com/sipeed/MaixPy/releases) 下载到适合 MaixCAM 的最新系统使用即可。
有些情况需要定制系统，比如：
* 比如你要量产 1k 个产品，都想放一个自己的应用，并且自动开机启动，不想一个一个配置，就可以改一下`builtin_files`，然后打包一个系统，所有板子一烧录就自带了自定义的文件，不要开及后再拷贝一次。
* 现在官方的系统没有你想要的软件包或者驱动，可以自己编译系统，选择自己想要的软件包编译定制的系统。

## 基础系统获取

原理是系统来自 [https://github.com/sipeed/LicheeRV-Nano-Build/releases](https://github.com/sipeed/LicheeRV-Nano-Build/releases) 作为基础系统（不能直接给 MaixCAM 烧录使用，否则有烧坏屏幕风险），然后将 MaixCAM 定制的相关文件拷贝到基础系统重新打包成 MaixCAM 能用的系统。

如果不需要对基础系统进行自定义，直接从 [https://github.com/sipeed/LicheeRV-Nano-Build/releases](https://github.com/sipeed/LicheeRV-Nano-Build/releases) 下载最新的系统镜像包即可。

如果基础系统无法满足你的要求，比如你需要自定义增删一些软件包和驱动等，按照 [https://github.com/sipeed/LicheeRV-Nano-Build](https://github.com/sipeed/LicheeRV-Nano-Build) README 文档进行编译， 尽量使用 docker 编译以避免遇到编译环境问题，以及使用`bash`，不要使用`zsh`。

注意编译出来的系统不能直接给 MaixCAM 烧录使用，否则有烧坏屏幕风险。


## 为 MaixCAM 拷贝文件

准备以下内容：
* 基础系统，是一个 `.img` 或者 `.img.xz` 文件。
* 对于 MaixCAM 还需要放一些额外的文件进去，到[MaixPy release](https://github.com/sipeed/MaixPy/releases) 下载最新的 `builtin_files.tar.xz` 文件。
> 如果你需要放一些自定义的文件进系统，可以解压后往目录里面填加，比如你想系统烧录后 `/root` 目录下就会有一个 `cat.jpg`， 那么就往这里 `root` 目录下放一个 `cat.jpg`。
* 下载或克隆 MaixPy 源码到本地。
* 编译 MaixPy 获得 `.whl` 安装包文件，你也可以到 [MaixPy release](https://github.com/sipeed/MaixPy/releases) 下载最新的安装包。

到`MaixPy/tools/os`目录下，执行
```shell
./gen_os.sh <base_os_filepath> <maixpy_whl_filepath> <builtin_files_dir_path> <skip_build_apps> <device_name>
```
这里参数说明：
* **base_os_filepath**: 基础系统路径, img 或者 img.xz 格式。
* **maixpy_whl_filepath**： MaixPy 软件包， whl 格式。
* **builtin_files_dir_path**： MaixCAM 自定义文件， 可以在 MaixPy release 下载到最新的。
* **os_version_str**: 系统版本，格式要满足类似 `maixcam-2024-08-16-maixpy-v4.4.21` 的规范。
* **skip_build_apps**: 跳过编译内置应用，可选参数，传 `1` 则会跳过，传 `0` 会将 MaixCDK 和 MaixPy 中的应用都编译并拷贝到系统中。
* **device name**: 可以选择`maixcam` 或者 `maixcam-pro`，对应了设备的型号。

举例：
```shell
./gen_os.sh '/home/xxx/.../LicheeRV-Nano-Build/install/soc_sg2002_licheervnano_sd/images/2024-08-13-14-43-0de38f.img' ../../dist/MaixPy-4.4.21-py3-none-any.whl '/home/xxx/.../maixcam_builtin_files' 0 maixcam-pro
```

等待编译内置应用以及拷贝完成，在 `MaixPy/tools/os/tmp` 目录下机会有一个`maixcam-pro-2024-08-15-maixpy-v4.4.21.img.xz`系统镜像了。

