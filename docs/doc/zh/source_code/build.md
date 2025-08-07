---
title: MaixCAM MaixPy 开发源代码指南
---

## 获取源代码

```shell
mkdir -p ~/maix
cd ~/maix
git clone https://github.com/sipeed/MaixPy
```

## 获取 MaixCDK 源码

MaixPy 项目依赖于 MaixCDK，需要先克隆它，放到电脑的某个目录（勿放在 MaixPy 目录下）

```shell
cd ~/maix
git clone https://github.com/sipeed/MaixCDK
```

然后需要设置环境变量 `MAIXCDK_PATH` 指定 MaixCDK 的路径，可以在 `~/.bashrc` 或者`~/.zshrc`（根据你使用的shell决定）添加：

```shell
export MAIXCDK_PATH=~/maix/MaixCDK
```

只有在成功设置环境变量后， MaixPy 才能找到 MaixCDK 源码。

## 构建并打包成 wheel 文件

```shell
cd ~/maix/MaixPy
python setup.py bdist_wheel maixcam
```

`maixcam` 可以被替换为其他板卡配置, 请查看 `MaixCDK/platforms` 目录。

构建成功后, 你会在 `dist` 目录中找到 wheel 文件, 传输到设备（开发板），在设备终端中使用 `pip install -U MaixPy****.whl` 在你的设备上安装或升级。

> `python setup.py bdist_wheel maixcam --skip-build` 不会执行构建命令, 只会打包 wheel 文件, 因此你可以先使用 `maixcdk menuconfig` 和 `maixcdk build` 来自定义构建。

> 另外如果你是在调试 API，需要频繁安装，使用 pip 安装会比较慢，可以直接编译后拷贝 `maix` 目录到设备的 `/usr/lib/python3.11/site-packages`目录下覆盖旧的文件即可。


## 手动构建

```shell
maixcdk build
```

## 修改源代码后运行测试

* 首先, 构建源代码
```shell
maixcdk build
```

* 如果为 PC 自身构建(平台 `linux`):
然后执行 `./run.sh your_test_file_name.py` 来运行 Python 脚本。
```shell
cd test
./run.sh examples/hello_maix.py
```

* 如果为板卡交叉编译:
  * 最快的方式是将 `maix` 目录复制到设备的 `/usr/lib/python3.11/site-packages/` 目录, 然后在设备上运行脚本。
  * 或者打包 wheel 文件并在设备上使用 `pip install -U MaixPy****.whl` 安装, 然后在设备上运行脚本。

## 本地预览文档

文档位于 [docs](https://github.com/sipeed/MaixPy/tree/main/docs) 目录, 使用 `Markdown` 格式, 你可以使用 [teedoc](https://github.com/teedoc/teedoc) 来生成网页版本的文档。

API 文档会在构建 MaixPy 固件时生成, **如果你没有构建 MaixPy, API 文档将会是空的**。

```shell
pip install teedoc -U
cd docs
teedoc install -i https://pypi.tuna.tsinghua.edu.cn/simple
teedoc serve
```

然后访问 `http://127.0.0.1:2333` 在网页浏览器中预览文档。

## 对于想要贡献的开发者

请查看 [MaixPy 开发源代码指南](./contribute.md)

如果在使用源代码时遇到任何问题, 请先参考 [FAQ](./faq.md)。
