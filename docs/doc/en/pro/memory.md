---
title: MaixPy MaixCAM Memory Usage Guide
---

## Introduction to MaixPy MaixCAM Memory

MaixPy is based on the Python language, which runs on a Linux system. The camera, images, models, and applications all require a large amount of memory. Since memory is limited, understanding memory usage and management methods is very important.

We can obtain the current memory usage status in many ways, either using built-in MaixPy methods or common Linux methods. For example, using Python:

```python
from maix import sys
print(sys.memory_info())
```

The output is similar to:

```json
{'cma_total': 0, 'cma_used': 0, 'cmm_total': 2147483648, 'cmm_used': 177512448, 'hw_total': 4294967296, 'total': 2060726272, 'used': 339562496}
```

Or

```python
import psutil

# Get virtual memory info
mem = psutil.virtual_memory()

print(f"Total memory: {mem.total / (1024 ** 3):.2f} GB")
print(f"Used memory: {mem.used / (1024 ** 3):.2f} GB")
print(f"Available memory: {mem.available / (1024 ** 3):.2f} GB")
print(f"Memory usage: {mem.percent}%")
```

You can also use command line tools like `cat /proc/meminfo` or the `free` command to see memory info.

From the `total` and `used` fields, you can see the total available memory and the memory already used.

Note that the memory shown here is the memory available to Linux user space, which is less than the actual physical memory. For example, for a MaixCAM2 device with 4GiB memory, the default shown here is 1GiB. Why this is so will be explained below.

---

## MaixPy MaixCAM Memory Layout

Because we use a Linux system, memory is divided into several regions based on usage:

| Region          | Purpose                                                                                                                                                                                                                                                                                                                                                    | Size                                                                                              |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| Reserved        | Low-level drivers and special purposes; varies by device and vendor                                                                                                                                                                                                                                                                                        | Varies by device, generally small                                                                 |
| Kernel Reserved | Memory reserved for the Linux kernel                                                                                                                                                                                                                                                                                                                       | Adjusted based on physical memory and kernel drivers, e.g., about 80MiB on MaixCAM2               |
| User Memory     | Used by Linux user-space programs                                                                                                                                                                                                                                                                                                                          | Adjusted based on physical memory and application needs, e.g., about 1.92GiB on MaixCAM2          |
| CMA Memory      | Contiguous Memory Allocator, used by Linux GPU/image components                                                                                                                                                                                                                                                                                            | Configured according to image-related applications                                                |
| CMM Memory      | Contiguous Memory Management, vendor- or user-defined contiguous memory region (not a Linux standard). Usually similar in purpose to CMA, but distinguished here as CMM. For example, MaixCAM series do not use standard CMA memory for images but define a custom region for camera, NPU, and other hardware drivers needing frequent large memory access | Allocated based on application needs, e.g., MaixCAM2 defaults to 1GiB, MaixCAM defaults to 128MiB |

The two types of memory to focus on are:

* **Linux User-Space Memory:** This is the total memory available for our code and applications, such as allocating arrays, creating objects, and loading programs.
* **CMM/CMA Memory:** For the MaixCAM series, without a GPU, CMA is usually zero (not used). Chip manufacturers tend to define their own standards. For example, MaixCAM and MaixCAM2 both use a custom memory region for camera, NPU, and other hardware drivers that need frequent large memory access. This improves performance and reduces memory fragmentation. For example:

  * **Camera frame capture:** The image is first read into this memory region; if the image needs to be viewed in Linux user space, it is mapped or copied into user space. Thus, the higher the camera resolution set by the application, the more memory is required.
  * **NPU running models:** Models are loaded into this custom memory area, not user space. For instance, if a large LLM model requires 1.5GiB, this memory area must be at least 1.5GiB to load the model successfully.

---

## Default Memory Sizes for Different Devices

| Device   | Hardware Memory Size | Linux Kernel + User Space | CMM Memory | CMA Memory |
| -------- | -------------------- | ------------------------- | ---------- | ---------- |
| MaixCAM  | 256MiB               | 151MiB                    | 105MiB     | 0MiB       |
| MaixCAM2 | 4GiB                 | 1GiB                      | 3GiB       | 0MiB       |
| MaixCAM2 | 1GiB                 | 512MiB                    | 512MiB     | 0MiB       |

---

## Adjusting Memory Allocation

As mentioned above, default values are generally sufficient for most applications. If you want to adjust sizes, for example to increase CMM memory for loading larger models, you can modify the allocation yourself.

Because CMM is typically designed by the CPU manufacturer, the modification methods differ by device:

* **MaixCAM:** The CMM memory is actually called ION memory by the vendor. Modifying it is complex and requires recompiling the system. See [GitHub modification reference](https://github.com/sipeed/LicheeRV-Nano-Build/commit/713161599e1b590249b1cd8a9e7f2a7f68d8d52d).
* **MaixCAM2:** The CMM memory is called CMM memory by the vendor. The MaixCAM2 image has been optimized so you only need to modify the `maix_memory_cmm` value in `/boot/configs` to the desired size in MiB. The default value is -1, which means using the default allocation.

---

If you need me to translate the content into a more formal technical document style or adapt it for a specific audience, let me know!

