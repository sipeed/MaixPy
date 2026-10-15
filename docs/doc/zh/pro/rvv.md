---
title: 使用RVV加速
---

## 简介

MaixPy 提供了 `rvv` Python 扩展模块，在支持 RISC-V 向量扩展（RVV）的 SG2002 / C906FDV 平台上，为 NumPy 兼容的向量与矩阵运算提供硬件加速；在没有 RVV 的平台上自动回退到标量实现。

- **模块名**：`rvv`
- **目标平台**：SG2002 / C906FDV，支持 RVV 0.7.1
- **数据类型**：仅支持 `float32`
- **设计目标**：
  - 直接接受 NumPy `ndarray` 或实现了 buffer protocol 的输入
  - 内部自动转换为内核期望的 `float32` + C 连续缓冲区
  - NumPy 可用时返回 `numpy.ndarray`（pybind11 `py::array_t<float>`）
  - 提供标量回退，使同一份源码可以在非 RISC-V 主机上构建和测试

源码仓库与发布说明见 [yangwenjie1231/sg2002_rvv](https://github.com/yangwenjie1231/sg2002_rvv)。

## 安装

在 MaixCAM 上安装预编译的 wheel 包：

```bash
pip install --force-reinstall ./clib/rvv-0.1.3-py3-none-any.whl
```

安装后可以这样检查 RVV 加速是否可用，并在不可用时降级到 CPU 计算：

```python
try:
    import rvv
    # 检查 rvv 模块是否有必要的函数
    if hasattr(rvv, 'add') and hasattr(rvv, 'sub') and hasattr(rvv, 'norm_l2'):
        _RVV_AVAILABLE = True
        print("✓ RVV 硬件加速可用")
    else:
        _RVV_AVAILABLE = False
        rvv = None
        print("⚠ rvv 模块存在但缺少必要函数，将使用 CPU 降级计算")
except ImportError:
    _RVV_AVAILABLE = False
    rvv = None
    print("⚠ rvv 模块不可用，将使用 CPU 降级计算")
```

> **注意**：wheel 本身不依赖 NumPy（`install_requires=[]`）。但若要传入 `numpy.ndarray`、或运行与 NumPy 的对比测试，需要在目标环境安装 NumPy。嵌入式 Linux 上通常无法编译/安装 NumPy。

## 性能对比

![RVV 与 NumPy 性能对比](../../assets/rvv_performance_comparison.jpg)

在 SG2002 上，`add` / `sub` / `scale` 这类逐元素运算更容易看到 RVV 带来的性能收益；`matmul` 是否快于 NumPy 取决于 NumPy 是否链接了高性能 BLAS（嵌入式环境中的 NumPy 常常没有，或性能有限）。

## 输入数据模型

`rvv` 的所有函数都基于 **buffer protocol**（PEP 3118）读取输入。

### 支持的输入类型

- `numpy.ndarray(dtype=np.float32)`
- 其他实现了 buffer protocol 的对象（如某些张量库 / 自定义 buffer）

### 强制要求

- **dtype 必须是 float32**
  - PEP 3118 `format == 'f'`
  - `itemsize == 4`
- **必须是 C-contiguous（行主序连续）**
  - 若为非连续 / 切片视图（stride 不满足连续布局），将抛出异常

### 自动转换规则

内部的 `as_f32_buffer()` 会优先尝试 NumPy 路径：

- `py::array_t<float, c_style | forcecast>`

这意味着：

- NumPy 可用时，传入 `float64` 或非连续数组会被复制/转换为连续的 `float32` 再计算。
- NumPy 不可用时，只能走通用 buffer 路径，此时不满足上述要求会直接报错。

如果你希望"零拷贝"并获得最佳性能，建议在调用前确保输入满足要求：

```python
x = np.ascontiguousarray(x, dtype=np.float32)
```

## API 参考

顶层模块名为 `rvv`，提供以下函数：

| 函数 | 说明 |
| --- | --- |
| `rvv.add(a, b)` | 1-D 逐元素加法 |
| `rvv.sub(a, b)` | 1-D 逐元素减法 |
| `rvv.scale(a, k)` | 1-D 向量按标量缩放 |
| `rvv.dot(a, b)` | 1-D 点积（内积） |
| `rvv.norm_l2(a)` | 1-D L2 范数 |
| `rvv.matmul(A, B)` | 2-D 矩阵乘法 |

### rvv.add(a, b) -> ndarray[float32]

**功能**：逐元素加法。

**参数**：

- `a`：1-D float32 buffer（期望 `ndim=1`）
- `b`：1-D float32 buffer（期望 `ndim=1`）

**返回**：1-D `float32` 数组，长度与 `a` 相同

**错误**：

- `ValueError`
  - `a` 或 `b` 维度不是 1：`a must have ndim=1, got ndim=...`
  - `a` 与 `b` 长度不同：`add: a and b must have the same length`
  - 输入不是 C-contiguous：`a must be C-contiguous float32 buffer`
- `TypeError`：输入不是 float32（`format != 'f'` 或 `itemsize != 4`）

**示例**：

```python
import numpy as np
import rvv

a = np.arange(8, dtype=np.float32)
b = np.ones(8, dtype=np.float32)
print(rvv.add(a, b))
```

### rvv.sub(a, b) -> ndarray[float32]

**功能**：逐元素减法，语义为 `out[i] = a[i] - b[i]`。

参数、返回值与错误同 `add`，两个向量长度必须一致。

```python
import numpy as np
import rvv

a = np.arange(8, dtype=np.float32)
b = np.ones(8, dtype=np.float32)
print(rvv.sub(a, b))
```

### rvv.scale(a, k) -> ndarray[float32]

**功能**：向量按标量缩放。

**参数**：

- `a`：1-D float32 buffer
- `k`：Python `float`

**返回**：1-D float32 数组

**错误**：`ValueError` / `TypeError`，校验规则同 `add`

```python
import numpy as np
import rvv

a = np.arange(8, dtype=np.float32)
print(rvv.scale(a, 0.5))
```

### rvv.dot(a, b) -> float

**功能**：点积（内积），语义为 `sum_i a[i] * b[i]`。

**参数**：

- `a`：1-D float32 buffer
- `b`：1-D float32 buffer

**返回**：Python `float`

**错误**：

- `ValueError`：长度不一致，`dot: a and b must have the same length`
- dtype / 连续性 / ndim 错误同上

```python
import numpy as np
import rvv

a = np.arange(8, dtype=np.float32)
print(rvv.dot(a, a))
```

### rvv.norm_l2(a) -> float

**功能**：L2 范数（欧几里得范数），定义为 `sqrt(dot(a, a))`。

**参数**：`a`：1-D float32 buffer

**返回**：Python `float`

**数值误差说明**：`dot` 和 `norm_l2` 都是归约（reduction）运算。当向量很大时（例如 1e6 长度），由于不同实现的归约顺序不同（RVV 分块、标量循环、NumPy/BLAS 向量化等），结果可能与 NumPy 有**很小的相对误差**。比较时建议使用相对误差（例如 `1e-4 ~ 1e-3`），而不是严格相等。

```python
import numpy as np
import rvv

a = np.random.randn(1000000).astype(np.float32)
print(rvv.norm_l2(a))
```

### rvv.matmul(A, B) -> ndarray[float32]

**功能**：矩阵乘法。

- 输入：`A` 形状 `(m, k)`，`B` 形状 `(k, n)`
- 输出：`C` 形状 `(m, n)`

**参数**：

- `A`：2-D float32 buffer（`ndim=2`，C-contiguous，行主序）
- `B`：2-D float32 buffer（`ndim=2`，C-contiguous，行主序）

**返回**：2-D float32 数组

**错误**：

- `ValueError`
  - 维度不是 2：`A must have ndim=2, got ndim=...`
  - 形状不匹配：`matmul: shape mismatch: A is (m,k) but B is (k2,n)`

```python
import numpy as np
import rvv

A = np.random.randn(2, 3).astype(np.float32)
B = np.random.randn(3, 4).astype(np.float32)
C = rvv.matmul(A, B)
print(C.shape)
```

### 组合使用示例

```python
import numpy as np
import rvv

a = np.arange(8, dtype=np.float32)
b = np.arange(8, dtype=np.float32)

print(rvv.add(a, b))
print(rvv.sub(a, b))
print(rvv.scale(a, 2.0))
print(rvv.dot(a, b))
print(rvv.norm_l2(a))

A = np.arange(6, dtype=np.float32).reshape(2, 3)
B = np.arange(12, dtype=np.float32).reshape(3, 4)
print(rvv.matmul(A, B))
```

## 常见错误与排查

### `... must be float32-compatible buffer ...`

说明输入不是 float32。解决：

```python
x = x.astype(np.float32, copy=False)
```

### `... must be C-contiguous float32 buffer`

说明输入是切片、转置等非连续视图。解决：

```python
x = np.ascontiguousarray(x, dtype=np.float32)
```

### `add/sub/dot: a and b must have the same length`

说明两个向量长度不一致。

## 性能建议

- 确保输入是 **float32** 且 **C-contiguous**，避免不必要的复制。
- 大数组上，`add` / `sub` / `scale` 通常更容易看到 RVV 的性能收益。
- `matmul` 是否快于 NumPy 取决于 NumPy 是否链接了高性能 BLAS（嵌入式环境中 NumPy 常常没有或性能有限）。

## 二次开发

本节面向需要在 SG2002 上自行构建、或基于本模块做二次开发的用户。

### 与实现对应关系

- Python 绑定：`rvv_ext/main/src/bind_rvv.cpp`
- C++ 公共接口声明：`rvv_ext/main/include/rvv.hpp`
- RVV 0.7.1 实现：`rvv_ext/main/src/rvv_rvv071.cpp`（仅在 `__riscv_vector` 下编译）
- 标量实现：`rvv_ext/main/src/rvv_scalar.cpp`

### 构建模式选择：交叉编译（MaixCAM） vs 主机测试（Linux）

项目在 `main/CMakeLists.txt` 中支持两类构建模式：

- **交叉编译到 SG2002（推荐）**：启用 `MaixCam`
  - 启用 RVV ISA flags（如 `-march=rv64imafdcv0p7xthead`）
  - 链接 SDK 的 `python3_lib_maixcam_musl_3.11.6` 头文件/库，避免 `Python.h` 缺失
- **主机 Linux 测试**：启用 `Linux`
  - 先尝试系统 `Python.h`（`python3-dev`），找不到则回退到 SDK python 组件

目标 Python 为 **3.11.6**（对应 SDK 组件 `python3_lib_maixcam_musl_3.11.6`）。

> 如果你看到 `fatal error: Python.h: No such file or directory`，说明当前构建模式没有拿到 Python 开发头文件。

### 构建注意事项

- 一定要在项目根目录 `rvv_ext/` 执行构建，不要在 `rvv_ext/main/` 里执行，否则会生成 `rvv_ext/main/build/...` 的配置，输出看起来像"无限循环"。
- 必须设置 SDK 环境变量 `MY_SDK_PATH`，不设置会报找不到 `/tools/cmds`。
- 交叉编译时 `TOOLCHAIN_PATH` **必须是绝对路径**，否则 CMake 会报 `TOOLCHAIN_PATH set error: ...`。
- `distclean` 会删除 `build/`，之后不能直接 `cmake --build build ...`，否则会报 `Error: could not load cache`，必须先重新执行 `python3 project.py build` 生成 `build/CMakeCache.txt`。
- 嵌入式 Linux 上通常**无法编译/安装 NumPy**。本库 wheel 安装不依赖 NumPy，但若要对比 NumPy 的结果/速度，需要目标环境能装 NumPy。
- `norm_l2` / `dot` 在超大向量（例如 1e6）上可能与 NumPy 有轻微差异（归约顺序导致的浮点误差），应使用相对误差比较，而不是严格相等。

### 使用 Auto-bind-Python-from-CC--main 构建

本项目使用与 `Auto-bind-Python-from-CC--main/examples/demo` 相同的构建系统。

**0) 设置 SDK 环境变量（必须）**

```bash
export MY_SDK_PATH=/root/xmusic/Auto-bind-Python-from-CC--main/Auto-bind-Python-from-CC--main
```

**1) 打开 menuconfig**

```bash
cd /root/xmusic/rvv_ext
python3 project.py menuconfig
```

**2) 配置工具链（交叉编译到 SG2002）**

- `-mcpu=c906fdv`
- `-march=rv64imafdcv0p7xthead`
- `-mcmodel=medany`
- `-mabi=lp64d`

也可以不用 menuconfig，直接通过参数配置：

```bash
python3 project.py config \
  --toolchain /root/xmusic/host-tools/gcc/riscv64-linux-musl-x86_64/bin \
  --toolchain-prefix riscv64-unknown-linux-musl-
```

或者使用项目顶级 `CMakeLists.txt` 读取的环境变量：

```bash
export MY_TOOLCHAIN_PATH=/root/xmusic/toolchains/maixcam/host-tools/gcc/riscv64-linux-musl-x86_64/bin
```

**3) 构建 + 生成 wheel 包**

```bash
python3 project.py build
```

产物：

- 编译的扩展：`build/main/libmain.so`
- Wheel 包：`dist/*.whl`

**4) 检查 RVV 是否启用（可选）**

执行 `python3 project.py build` 后，检查构建日志中的编译命令行是否包含：

- `-march=rv64imafdcv0p7xthead`

如果存在该标志，`__riscv_vector` 应该已被定义，RVV 实现（`rvv_rvv071.cpp`）会被编译进库。

### IDE 代码提示

`rvv` 是二进制扩展模块（`rvv.so`），IDE 无法像纯 Python 那样从源码推断函数签名。本项目已通过 **PEP 561** 提供类型提示：

- `rvv_ext/rvv.pyi`：模块存根（stub），为 `add/sub/scale/dot/norm_l2/matmul` 提供签名与说明
- `rvv_ext/py.typed`：标记文件，告知工具/IDE 该包携带类型信息

打包 wheel 时这两者会一并打入（见 `rvv_ext/setup.py`）。

**方式 A：安装 wheel 后获得提示（推荐）**

```bash
pip install --no-deps --force-reinstall dist/*.whl
```

**方式 B：在源码目录直接开发时获得提示**

- 确保 IDE 的解释器/项目索引能看到 `rvv_ext/rvv.pyi`
- 可在 PyCharm 中将 `rvv_ext/` 目录标记为 **Sources Root**（或加入 `PYTHONPATH`）

> 无论哪种方式，运行时导入仍然是 `import rvv`。

### 测试

测试位于 `rvv_ext/tests` 目录，需要 NumPy + pytest：

```bash
pytest -q
```

不依赖 pytest 的性能对比脚本：

```bash
python3 tests/test_rvv.py
```

在 SG2002 上还可以运行微基准测试：

```bash
python3 tests/bench_perf.py
```

### 故障排除

**`Error: could not load cache`**

在执行 `cmake --build build ...` 时出现，说明 CMake 缓存（`build/CMakeCache.txt`）缺失。常见原因：

- 执行了 `python3 project.py distclean`，之后**没有**重新运行 CMake 配置步骤
- `build/` 目录被删除或为空

解决方法：

```bash
cd /path/to/rvv_ext

# 重新运行配置（生成 build/CMakeCache.txt）
python3 project.py build

# 然后编译
cmake --build build --target main -- -j"$(nproc)"
```

**`setup.py` 显示 `Native library not found: build/main/libmain.so`**

说明扩展还没有构建，或者被构建到了其他目录。检查：

```bash
find build -maxdepth 4 -name 'libmain.so' -o -name '*.so' | sort
```

如果 `libmain.so` 存在但不在 `build/main/` 下，请相应调整 `setup.py` 中的 `SO_FILE_PATH`。

### 复制粘贴命令（嵌入式 Linux）

```bash
cd /path/to/rvv_ext            # 根据实际路径调整

# (可选) 完全清理：会移除 build/ 和 CMakeCache.txt
python3 project.py distclean

# 1) 配置 CMake（重新创建 build/ 和 build/CMakeCache.txt）
python3 project.py build

# 健全性检查（配置后应该存在）
ls -la build/CMakeCache.txt

# 2) 编译扩展共享库（创建 build/main/libmain.so）
cmake --build build --target main -- -j"$(nproc)"

# 健全性检查（编译后应该存在）
ls -la build/main/libmain.so

# 3) 构建 wheel 包（创建 dist/*.whl）
python3 setup.py bdist_wheel

# 4) 列出 wheel 包
ls -la dist
```

> 如果只想清理编译产物但保留 CMake 缓存，优先使用 `python3 project.py clean` 而不是 `distclean`。

## 许可

本项目采用 LGPL-3.0 许可，详见仓库中的 LICENSE 文件。

Copyright (C) 2026 ywj &lt;yangwenjie1231@qq.com&gt;
