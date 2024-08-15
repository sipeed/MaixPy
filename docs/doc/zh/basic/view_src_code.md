---
title: MaixCAM MaixPy 如何找到 MaixPy API 对应的源码
---

## 简介

MaixPy 是基于 Python 实现，有部分函数是用 Python 编写，大多数底层代码都是使用 C/C++ 编写，这样可以保证运行效率。

如果我们在使用一个函数遇到疑问，我们可以查询本文档，以及 API 文档。
如果仍然不能解决你的疑惑，那么可以直接按照本文的方法找到底层实现的源码找出答案，**也欢迎一起贡献文档或代码，成为 MaixPy 开发者的一员**！

## 先看文档

一定要先看文档： [https://wiki.sipeed.com/maixpy/](https://wiki.sipeed.com/maixpy/), 然后看 API 文档：[https://wiki.sipeed.com/maixpy/api/index.html](https://wiki.sipeed.com/maixpy/api/index.html)

API 文档只有英文，原因是 API 文档是从代码的注释生成而来，代码中一律使用英文，看不懂英文可以使用翻译。


## 如何找到 API 对应的源码

首先有两个开源仓库，分别是 [MaixPy](https://github.com/sipeed/MaixPy) 和 [MaixCDK](https://github.com/sipeed/MaixCDK)。
MaixPy 是工程仓库，里面包含了 MaixPy 的部分源码，所有文档、例程；MaixCDK 包含了大多数 MaixPy API 的底层 C/C++ 实现。

我们可以把这两份代码下载下来，也可以直接在网页查看。

**顺便记得给它们点一个 star 让更多人看到哦～**

### 找到 C/C++ 编写的 API

现在假设我们要找到 `maix.image.Image.find_blobs` 函数为例， 首先我们尝试手动去找：

* 因为这是属于视觉相关的 API， 我们在 [MaixCDK](https://github.com/sipeed/MaixCDK) 的`components/vision/include` 下面可以看到有一个 `maix_image.hpp`的头文件，猜测大概在这里面。
* 在`maix_image.hpp` 搜索 `find_blobs`，马上就发现了函数声明：
```c++
std::vector<image::Blob> find_blobs(std::vector<std::vector<int>> thresholds = std::vector<std::vector<int>>(), bool invert = false, std::vector<int> roi = std::vector<int>(), int x_stride = 2, int y_stride = 1, int area_threshold = 10, int pixels_threshold = 10, bool merge = false, int margin = 0, int x_hist_bins_max = 0, int y_hist_bins_max = 0);
```
* 同时我们发现函数声明前面有注释，API 文档即从这份注释自动生成而来，如果你仔细对比 API 文档和这个注释会发现他们一模一样的，改动这个注释编译后会产生 API 文档。
* 这只是函数声明，我们找到`components/vision/src/maix_image.cpp`，发现里面没有这个函数，仔细一看有个`components/vision/src/maix_image_find_blobs.cpp`，原来是将函数单独写了一个`cpp`，在里面我们就能看到函数的源代码了。

### 找到使用 Pybind11 编写的 API

如果 MaixCDK 里面找不到，那就可以到 [MaixPy/components](https://github.com/sipeed/MaixPy/tree/main/components)里面寻找。

> 上面的代码你会发现，我们在使用`find_blobs`时第一个参数是`[[...]]`这样的参数即`list`类型，C/C++ 定义第一个参数是`std::vector<std::vector<int>>`类型，原因是我们使用了`pybind11`自动将 `std::vector` 类型转换为了`list`类型。
而有一些类型在`MaixCDK`里面不方便定义，比如`numpy`的`array`类型，但是`pybind11`里面有相关的定义方便我们直接使用，但是又不想 MaixCDK 里面有 pybind11 相关的代码，所以我们在[MaixPy/components](https://github.com/sipeed/MaixPy/tree/main/components) 里面来写使用了 `pybind11` 相关的代码，比如`maix.image.image2cv`方法。

## 如何修改代码

在找到代码后，直接修改，然后按照[编译文档](../source_code/build.md)编译出固件即可。

## 如何增加代码

照抄其它 API，写一个函数，然后添加完整的注释，注释中额外添加一个`@maixpy maix.xxx.xxx`，这里`xxx`即你想添加到的模块和`API`名，然后编译出固件即可。

可以参考[MaixCDK/components/basic/includemaix_api_example.hpp](https://github.com/sipeed/MaixCDK/blob/master/components/basic/include/maix_api_example.hpp)。

API 参数和返回值用基础的`C++` 类型会自动转换为`Python`的类型，是不是十分简单.
具体的类型转换参考[pybind11 类型自动转换列表](https://pybind11.readthedocs.io/en/stable/advanced/cast/overview.html#conversion-table)

比如我们希望增加一个`maix.my_module.my_func`，在`MaixCDK`中合适的地方（最好符合现在的文件夹分类）创建一个头文件，然后添加代码：
```cpp
namespace maix::my_module
{
    /**
     * My function, add two integer.
     * @param a arg a, int type
     * @param b arg b, int type
     * @return int type, will a + b
     * @maixpy maix.my_module.my_func
     */
    int my_func(int a, int b);
}
```

然后增加一个`cpp`文件：
```cpp
int my_func(int a, int b)
{
    return a + b;
}
```

然后编译 MaixPy 生成`whl`文件，安装到设备即可使用`maix.my_module.my_func`函数。


## 如何贡献代码

如果你发现 MaixPy 有未完成的 API， 或者有 bug， 欢迎修改后提交 PR（Pull Request）到 MaixPy 仓库，具体提交方法看 [贡献文档和代码](../source_code/contribute.md)




