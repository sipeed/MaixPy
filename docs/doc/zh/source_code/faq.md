MaixPy 源代码常见问题
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
