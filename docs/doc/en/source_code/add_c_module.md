---
title: Adding a C/C++ Module to MaixCAM MaixPy
---

## Introduction

Sometimes you need to execute a function efficiently, and Python's speed is insufficient. In such cases, you can implement the function using C/C++ or other compiled languages.

## General Function Wrapping

If the function you want to wrap does not depend on other features of MaixPy, you can directly use the general methods for adding modules to Python using C/C++. You can search for methods like `ffi` or `ctype` on the internet.
> PRs are welcome to add more methods.

## If Your Module Needs to Depend on Other MaixPy Basic APIs

### Method 1

Directly modify the MaixPy firmware and then compile it. Refer to [View MaixPy API Source Code](../basic/view_src_code.md). This method is the simplest and fastest. If the code is well-packaged, it can be merged into the official repository (by submitting a PR).

* Follow [Compiling MaixPy Source Code](./build.md) to get the `dist/***.whl` installation package.
* Send the `.whl` package from the `dist` directory to the device, then run the code `import os; os.system("pip install /root/xxxxx.whl")` (replace the path accordingly).
* If installing the `.whl` package is too slow during debugging, you can use `maixcdk build` to compile and then use `scp -r maix_xxx root@10.228.104.1:/usr/lib/python3.11/site-packages` to directly copy it to the device system to overwrite the package. Adjust the package name and device IP as needed.
* Once you have finished debugging and feel that the features you added are valuable, consider merging them into the official repository. You can learn how to do this by searching for keywords like "github submit PR" on search engines.

Modifying the code:
As described in [View MaixPy API Source Code](../basic/view_src_code.md), you can view and modify the source code, add C++ functions, and include comments. After compiling, you can call them in MaixPy. It's very simple.

For example:
```cpp
namespace maix::test
{
    /**
     * My function, add two integers.
     * @param a arg a, int type
     * @param b arg b, int type
     * @return int type, a + b
     * @maixpy maix.test.add
     */
    int add(int a, int b);
}
```

Yes, simply write a C++ function. Note the `@maixpy` comment. During compilation, a Python function will be automatically generated. It's that simple! Then you can call the function with `maix.test.add(1, 2)`.

### Method 2

Create a MaixPy module project based on an engineering template. This method is suitable for adding a package without modifying the MaixPy source code and still using MaixPy (MaixCDK) APIs. The method is as follows:

* First, [compile MaixPy source code](./build.md) to ensure the compilation environment is set up correctly.
* Copy the [MaixPy/tools/maix_module](https://github.com/sipeed/MaixPy/tree/main/tools/maix_module) project template to a new directory. It can be in the same directory as `MaixPy`. For example, copy all files and directories to the `maix_xxx` directory.
* In the `maix_xxx` directory, run `python init_files.py` in the terminal to initialize the project files.
* Change the project name: Modify the `module_name.txt` file to the desired module name, starting with `maix_`. This makes it easier for others to find your project on [pypi.org](https://pypi.org) or [github.com](https://github.com).
* Run `python setup.py bdist_wheel linux` in the project root directory to build for the computer.
* After building, you can directly run `python -c "import maix_xxx; maix_xxx.basic.print('Li Hua')"` in the project root directory to test your module functions.
* Run `python setup.py bdist_wheel maixcam` to build the package for `MaixCAM`. Note that the code prompt file (pyi file) can only be generated when building for the `linux` platform. Therefore, before releasing, first build for the `linux` platform to generate the code prompt file, then execute this command to generate the package for the `MaixCAM` platform.
* Send the `.whl` package from the `dist` directory to the device, then run `import os; os.system("pip install /root/xxxxx.whl")` (replace the path accordingly).
* If installing the `.whl` package is too slow during debugging, you can use `maixcdk build` to compile and then use `scp -r maix_xxx root@10.228.104.1:/usr/lib/python3.11/site-packages` to directly copy it to the device system to overwrite the package. Adjust the package name and device IP as needed.
* Once you have debugged your code, consider open-sourcing it on [github.com](https://github.com) and uploading it to [pypi.org](https://pypi.org). You can refer to the official documentation or search for tutorials on how to upload. Generally, you need to run `pip install twine` and then `twine upload dist/maix_xxx***.whl`. After completing this, feel free to share your achievements on [maixhub.com/share](https://maixhub.com/share)!

Modifying the code:
As described in [View MaixPy API Source Code](../basic/view_src_code.md), add source files in the `components/maix/include` and `components/maix/src` directories, add C++ functions, and include comments. After compiling, you can call them directly. It's very simple.

For example:

```cpp
namespace maix_xxx::test
{
    /**
     * My function, add two integers.
     * @param a arg a, int type
     * @param b arg b, int type
     * @return int type, a + b
     * @maix_xxx maix_xxx.test.add
     */
    int add(int a, int b);
}
```

Yes, simply write a C++ function. Note the `@maix_xxx` comment. During compilation, a Python function will be automatically generated. It's that simple! Then you can call the function with `maix_xxx.test.add(1, 2)`.


