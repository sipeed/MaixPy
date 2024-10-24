---
title: 给 MaixCAM MaixPy 添加一个 C/C++ 模块
---

## 简介

有时候需要高效地执行某个函数， Python 的速度无法满足时，就可以使用 C/C++ 或者其它编译型语言来实现。


## 通用函数封装

如果你想封装的函数实现的功能不依赖 MaixPy 的其它功能，直接使用 Python 使用 C/C++ 添加模块的通用方法，具体方法可以自行百度，比如 ffi， ctype 等
> 欢迎 PR 添加方法

## 如果你的模块还想依赖 MaixPy 的其它基础 API

### 方法一

直接修改 MaixPy 固件，然后编译过即可，参考 [查看 MaixPy API 源码](../basic/view_src_code.md)，这种方法最简单快捷，如果代码封装好了还能合并到官方仓库（提交 PR）。

* 按照[编译 MaixPy 源码](./build.md) 通过即可获得`dist/***.whl`安装包。
* 将`dist`目录下的`.whl`包发送到设备，然后使用运行代码`import os;os.system("pip install /root/xxxxx.whl")`即可（替换路径）。
* 如果调试的时候觉得安装 `.whl` 包太慢了，可以使用`maixcdk build` 编译，然后使用`scp -r maix_xxx root@10.228.104.1:/usr/lib/python3.11/site-packages`直接拷贝到设备系统种覆盖包，这里需要根据你的包名和设备 ip 替换一下。
* 当你调试好后如果觉得自己填加的功能不错，可以考虑合并到官方的仓库，具体方法可以搜索引擎搜索"github 提交 PR"相关关键词学习。

修改代码：
正如 [查看 MaixPy API 源码](../basic/view_src_code.md) 问种所描述的查看和修改源码的方式，增加 C++ 函数，并且填加注释，然后编译后 MaixPy 中就能调用了，非常简单。

比如：
```cpp
namespace maix::test
{
    /**
     * My function, add two integer.
     * @param a arg a, int type
     * @param b arg b, int type
     * @return int type, will a + b
     * @maixpy maix.test.add
     */
    int add(int a, int b);
}
```

没错，直接写一个 C++ 语法的函数，注意这里加了一个`@maixpy` 的注释，编译时会自动生成 Python 函数，就是这么简单！
然后就能通过`maix.test.add(1, 2)` 来调用函数了。

### 方法二

基于工程模板创建一个 MaixPy 模块工程，这种方法适用于不想改动 MaixPy 源码，希望单独加一个包，并且还能用上 MaixPy（MaixCDK）的 API 的情况。方法如下：

* 首先[编译 MaixPy 源码](./build.md) 通过，保证我们的编译环境没问题。
* 复制一份 [MaixPy/tools/maix_module](https://github.com/sipeed/MaixPy/tree/main/tools/maix_module) 工程模板到一个新的目录，可以和`MaixPy`放在同一个目录。比如将所有文件和目录复制到了`maix_xxx` 目录下。
* 在`maix_xxx`目录下，终端执行`python init_files.py`来初始化项目文件。
* 修改项目名：修改`module_name.txt` 文件，改成你要的模块名称，必须以`maix_`开头，这样方便其它用户能在 [pypi.org](https://pypi.org) 或者 [github.com](https://github.com) 搜索到你的项目。
* 和 MaixPy 一样执行`python setup.py bdist_wheel linux` 就可以开始为电脑构建。
* 构建完成后可以直接在项目根目录执行`python -c "import maix_xxx;maix_xxx.basic.print('Li Hua')"`就能运行你的模块函数了。
* 执行`python setup.py bdist_wheel maixcam` 就可以为`MaixCAM` 构建软件包了。需要注意的是，构建过程种的代码提示文件(pyi文件)只能在给`linux` 平台构建的时候生成，所以在正式发布的时候需要先执行上一步的`linux`平台构建生成代码提示文件，然后再执行本步的命令生成`MaixCAM`平台的软件包。
* 将`dist`目录下的`.whl`包发送到设备，然后使用运行代码`import os;os.system("pip install /root/xxxxx.whl")`即可（替换路径）。
* 如果调试的时候觉得安装 `.whl` 包太慢了，可以使用`maixcdk build` 编译，然后使用`scp -r maix_xxx root@10.228.104.1:/usr/lib/python3.11/site-packages`直接拷贝到设备系统种覆盖包，这里需要根据你的包名和设备 ip 替换一下。
* 当你调试好代码后，可以考虑将代码开源到[github.com](https://github.com)，并且上传到[pypi.org](https://pypi.org)（具体上传方法可以看官方文档或者搜索教程，大概就是`pip install twine`然后 `twine upload dist/maix_xxx***.whl`就可以了。），写好后欢迎到[maixhub.com/share](https://maixhub.com/share)来分享告诉大家你的成果！

修改代码：
正如 [查看 MaixPy API 源码](../basic/view_src_code.md) 问种所描述的查看和修改源码的方式，在`components/maix/include` 和 `components/maix/src` 下增加源文件，增加 C++ 函数，并且填加注释，然后编译后就直接能调用了，非常简单。
比如:

```cpp
namespace maix_xxx::test
{
    /**
     * My function, add two integer.
     * @param a arg a, int type
     * @param b arg b, int type
     * @return int type, will a + b
     * @maix_xxx maix_xxx.test.add
     */
    int add(int a, int b);
}
```

没错，直接写一个 C++ 语法的函数，注意这里加了一个`@maix_xxx` 的注释，编译时会自动生成 Python 函数，就是这么简单！
然后就能通过`maix_xxx.test.add(1, 2)` 来调用函数了。




