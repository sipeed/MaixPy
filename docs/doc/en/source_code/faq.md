MaixCAM MaixPy Source Code FAQ
===

## subprocess.CalledProcessError: Command '('lsb_release', '-a')' returned non-zero exit status 1.

Edit `/usr/bin/lsb_release` as root, change the first line from `#!/usr/bin/python3` to `python3`.

Then compile again and it should work.

## ImportError: arg(): could not convert default argument 'format: maix::image::Format' in method '<class 'maix._maix.camera.Camera'>.__init__' into a Python object (type not registered yet?)

Pybind11 need you to register `image::Format` first, then you can use it in `camera::Camera`, to we must fist define `image::Format` in generated `build/maixpy_wrapper.cpp` source file.

To achieve this, edit `components/maix/headers_priority.txt`, the depended on should be placed before the one use it.
e.g.
```
maix_image.hpp
maix_camera.hpp
```

## /usr/bin/ld: /lib/libgdal.so.30: undefined reference to `std::condition_variable::wait(std::unique_lock<std::mutex>&)@GLIBCXX_3.4.30' collect2: error: ld returned 1 exit status

This issue commonly arises when building for Linux and using a conda environment, due to some libraries in the conda environment having compilation parameter problems. The solution is to not use conda, or to individually locate the problematic library within conda and replace it with the system's version or simply delete it (the system will then locate the necessary library).

