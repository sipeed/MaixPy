---
title: MaixCAM MaixPy How to Find the Source Code Corresponding to MaixPy API
---

## Introduction

MaixPy is implemented based on Python, with some functions written in Python and most of the underlying code written in C/C++. This ensures efficient performance.

If you have questions while using a function, you can consult this document and the API documentation. If your doubts are still unresolved, you can find the underlying implementation source code using the method described in this article. **You are also welcome to contribute to the documentation or code, and become a MaixPy developer!**

## Check the Documentation First

Always check the documentation first: [https://wiki.sipeed.com/maixpy/](https://wiki.sipeed.com/maixpy/), then check the API documentation: [https://wiki.sipeed.com/maixpy/api/index.html](https://wiki.sipeed.com/maixpy/api/index.html).

The API documentation is only available in English because it is generated from the comments in the code, which are all in English. If you can't understand English, you can use a translation tool.

## How to Find the Source Code Corresponding to the API

There are two open-source repositories: [MaixPy](https://github.com/sipeed/MaixPy) and [MaixCDK](https://github.com/sipeed/MaixCDK). MaixPy is the project repository containing part of the MaixPy source code, all documents, and examples; MaixCDK contains most of the underlying C/C++ implementations of MaixPy APIs.

You can download these two repositories or view them directly on the web.

**Don't forget to give them a star so more people can see it!**

### Finding C/C++ Written APIs

Assume we want to find the `maix.image.Image.find_blobs` function as an example. First, let's try to find it manually:

* Since this is a vision-related API, we look in the `components/vision/include` directory of [MaixCDK](https://github.com/sipeed/MaixCDK) and see a `maix_image.hpp` header file, where we might find it.
* Searching for `find_blobs` in `maix_image.hpp`, we immediately find the function declaration:
```c++
std::vector<image::Blob> find_blobs(std::vector<std::vector<int>> thresholds = std::vector<std::vector<int>>(), bool invert = false, std::vector<int> roi = std::vector<int>(), int x_stride = 2, int y_stride = 1, int area_threshold = 10, int pixels_threshold = 10, bool merge = false, int margin = 0, int x_hist_bins_max = 0, int y_hist_bins_max = 0);
```
* We also notice that there are comments before the function declaration, from which the API documentation is automatically generated. If you compare the API documentation with this comment, you will find them identical. Modifying this comment and recompiling will generate updated API documentation.
* This is just the function declaration. We find that there is no such function in `components/vision/src/maix_image.cpp`. However, we see `components/vision/src/maix_image_find_blobs.cpp`, indicating that the function is written in a separate `cpp` file. Here, we can see the function's source code.

### Finding APIs Written with Pybind11

If you can't find it in MaixCDK, look in [MaixPy/components](https://github.com/sipeed/MaixPy/tree/main/components).

> In the above code, you'll notice that the first parameter we use in `find_blobs` is of type `list`, i.e., `[[...]]`, while the C/C++ definition is `std::vector<std::vector<int>>`. This is because we use `pybind11` to automatically convert the `std::vector` type to `list` type.
For some types like `numpy`'s `array`, which are inconvenient to define in MaixCDK, we use the `pybind11` definitions in [MaixPy/components](https://github.com/sipeed/MaixPy/tree/main/components). For example, the `maix.image.image2cv` method uses `pybind11` related code here.

## How to Modify the Code

After finding the code, modify it directly and compile the firmware following the [build documentation](../source_code/build.md).

## How to Add Code

Copy other APIs, write a function, and add complete comments. Include an extra `@maixpy maix.xxx.xxx` tag in the comments, where `xxx` is the module and API name you want to add. Then compile the firmware.

Refer to [MaixCDK/components/basic/includemaix_api_example.hpp](https://github.com/sipeed/MaixCDK/blob/master/components/basic/include/maix_api_example.hpp).

API parameters and return values automatically convert from basic `C++` types to Python types, making it very simple. See the [pybind11 automatic type conversion list](https://pybind11.readthedocs.io/en/stable/advanced/cast/overview.html#conversion-table) for details.

For example, to add `maix.my_module.my_func`, create a header file in the appropriate place in MaixCDK (preferably following the current folder classification) and add the code:
```cpp
namespace maix::my_module
{
    /**
     * My function, add two integers.
     * @param a arg a, int type
     * @param b arg b, int type
     * @return int type, will return a + b
     * @maixpy maix.my_module.my_func
     */
    int my_func(int a, int b);
}
```

Then add a `cpp` file:
```cpp
int my_func(int a, int b)
{
    return a + b;
}
```

Compile MaixPy to generate the `whl` file and install it on the device to use the `maix.my_module.my_func` function.

## How to Contribute Code

If you find any unfinished APIs or bugs in MaixPy, feel free to submit a PR (Pull Request) to the MaixPy repository. For detailed submission methods, see [Contributing Documentation and Code](../source_code/contribute.md).

