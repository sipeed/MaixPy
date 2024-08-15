MaixCAM MaixPy 源代码常见问题
===

## subprocess.CalledProcessError: Command '('lsb_release', '-a')' returned non-zero exit status 1.

以 root 身份编辑 `/usr/bin/lsb_release`，将第一行从 `#!/usr/bin/python3` 更改为 `python3`。

然后重新编译,应该就可以工作了。

## ImportError: arg(): could not convert default argument 'format: maix::image::Format' in method '<class 'maix._maix.camera.Camera'>.**init**' into a Python object (type not registered yet?)

Pybind11 需要你先注册 `image::Format`，然后才能在 `camera::Camera` 中使用它,所以我们必须先在生成的 `build/maixpy_wrapper.cpp` 源文件中定义 `image::Format`。

要实现这一点,请编辑 `components/maix/headers_priority.txt`,被依赖的应该放在依赖它的前面。
例如:
```
maix_image.hpp
maix_camera.hpp
```

## /usr/bin/ld: /lib/libgdal.so.30: undefined reference to `std::condition_variable::wait(std::unique_lock<std::mutex>&)@GLIBCXX_3.4.30' collect2: error: ld returned 1 exit status

一般在为 Linux 构建时并且使用 conda 环境时容易出现，conda 环境中的一些库编译参数问题，解决方法就是不用 conda 即可， 或者单独找到 conda 中的那个库，替换成系统的或者直接删掉（会从系统找）

