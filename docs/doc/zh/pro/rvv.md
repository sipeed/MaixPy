---
title: 使用RVV加速
---
## License

Copyright (C) 2026 ywj <yangwenjie1231@qq.com>

This library is free software; you can redistribute it and/or modify it
under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library.  If not, see <https://www.gnu.org/licenses/>.

SPDX-License-Identifier: LGPL-3.0

# sg2002_rvv v0.1.0 — 首次开源发布
仓库地址：[https://github.com/yangwenjie1231/sg2002_rvv/releases](https://github.com/yangwenjie1231/sg2002_rvv/releases)记得给个star，手动狗头
发布日期：2026-03-03

概述
本次发布公开了 sg2002_rvv 的实现、示例、测试与文档。项目旨在为 RISC‑V 向量扩展（RVV）相关研究与工程提供参考实现与可复现的基准。

主要变更
- 初始开源：公开 src/, examples/, scripts/, docs/
- 添加础构建脚本与单元测试
- 提供性能基准脚本与示例数据

许可
本仓库采用LGPL3.0 许可（请见 LICENSE 文件）。

贡献
欢迎通过 Issues 和 Pull Requests 参与贡献。详细指南请见 CONTRIBUTING.md。

联系方式
维护者：yangwenjie1231（https://github.com/yangwenjie1231）
# 性能对比
![](https://maixhub.com/public/sharing/24278-2a9ef5bc220a4c0d8fc973c12f55f93f.jpg)
- 导入示例
```python
try:
    import rvv
    # 检查rvv模块是否有必要的函数
    if hasattr(rvv, 'add') and hasattr(rvv, 'sub') and hasattr(rvv, 'norm_l2'):
        _RVV_AVAILABLE = True
        print("✓ RVV硬件加速可用")
    else:
        _RVV_AVAILABLE = False
        rvv = None
        print("⚠ RVV模块存在但缺少必要函数，将使用CPU降级计算")
except ImportError:
    _RVV_AVAILABLE = False
    rvv = None
    print("⚠ RVV模块不可用，将使用CPU降级计算，并尝试自动安装RVV依赖")
    try:
        import os
        os.system('pip install --force-reinstall ./clib/rvv-0.1.3-py3-none-any.whl')
        try:
            import rvv
            _RVV_AVAILABLE = True
            print("✓ RVV模块已安装，将使用RVV硬件加速")
        except ImportError:
            print("⚠ RVV模块安装后启动失败，请手动安装")
    except ImportError:
        print("⚠ 无法自动安装RVV依赖，请手动安装")

```

# rvv API 文档（SG2002 / C906FDV / RVV 0.7.1）

本文档描述 `rvv` Python 扩展模块的公共 API。

- 模块名：`rvv`
- 目标平台：RISC-V（SG2002 / C906FDV），支持 RVV 0.7.1 时会启用矢量加速
- 数据类型：**仅支持 float32**
- 设计目标：
  - **兼容 NumPy 的 N 维数组（ndarray）作为输入**
  - 在内部自动转换为适合 RVV/kernel 处理的格式（float32 + C 连续）
  - 在 NumPy 可用时返回 `numpy.ndarray`（pybind11 `py::array_t<float>`）
- 编译参考：基于[https://github.com/Taoxuan-168/Auto-bind-Python-from-CC-](https://github.com/Taoxuan-168/Auto-bind-Python-from-CC-)并修改了部分代码
> 安装提示：wheel 本身不依赖 NumPy（`install_requires=[]`）。
> 但若要传入 `numpy.ndarray`、或运行与 NumPy 的对比测试，需要目标环境安装 NumPy。

---

## 1. 输入数据模型（重要）

`rvv` 的所有函数都基于 **buffer protocol**（PEP 3118）读取输入。

### 1.1 支持的输入类型

以下输入通常都可以：

- `numpy.ndarray(dtype=np.float32)`
- 其他实现了 buffer protocol 的对象（如某些张量库/自定义 buffer）

### 1.2 强制要求

- **dtype 必须是 float32**
  - PEP3118 `format == 'f'`
  - `itemsize == 4`
- **必须是 C-contiguous（行主序连续）**
  - 若为非连续/切片视图（stride 不满足连续布局），将抛出异常

### 1.3 自动转换规则

内部的 `as_f32_buffer()` 会优先尝试 NumPy 路径：

- `py::array_t<float, c_style | forcecast>`

这意味着：

- 如果 NumPy 可用，且你传入 `float64` 或非连续数组，它会复制/转换为连续的 `float32` 再计算。
- 如果 NumPy 不可用，则只能走通用 buffer 路径，此时不满足上述要求会直接报错。

---

## 2. 向量运算 API（1-D）

### 2.1 `rvv.add(a, b) -> ndarray[float32]`

**功能**：逐元素加法。

**参数**：

- `a`：1-D float32 buffer（期望 `ndim=1`）
- `b`：1-D float32 buffer（期望 `ndim=1`）

**返回**：

- `out`：1-D `float32` 数组，长度与 `a` 相同

**错误**：

- `ValueError`：
  - `a` 或 `b` 维度不是 1：`"a must have ndim=1, got ndim=..."`
  - `a` 与 `b` 长度不同：`"add: a and b must have the same length"`
  - 输入不是 C-contiguous：`"a must be C-contiguous float32 buffer"`
- `TypeError`：
  - 输入不是 float32：例如 `format!='f'` 或 `itemsize!=4`

**示例**：

```python
import numpy as np
import rvv

a = np.arange(8, dtype=np.float32)
b = np.ones(8, dtype=np.float32)
print(rvv.add(a, b))
```

---

### 2.2 `rvv.sub(a, b) -> ndarray[float32]`

**功能**：逐元素减法。

- 语义：`out[i] = a[i] - b[i]`
- 参数/返回/错误与 `add` 相同，长度必须一致。

**示例**：

```python
import numpy as np
import rvv

a = np.arange(8, dtype=np.float32)
b = np.ones(8, dtype=np.float32)
print(rvv.sub(a, b))
```

---

### 2.3 `rvv.scale(a, k) -> ndarray[float32]`

**功能**：向量按标量缩放。

**参数**：

- `a`：1-D float32 buffer
- `k`：Python `float`

**返回**：

- `out`：1-D float32 数组

**错误**：

- `ValueError` / `TypeError`：同 `add` 的 dtype/contiguous/ndim 校验

**示例**：

```python
import numpy as np
import rvv

a = np.arange(8, dtype=np.float32)
print(rvv.scale(a, 0.5))
```

---

### 2.4 `rvv.dot(a, b) -> float`

**功能**：点积（内积）。

- 语义：`sum_i a[i] * b[i]`

**参数**：

- `a`：1-D float32 buffer
- `b`：1-D float32 buffer

**返回**：

- Python `float`

**错误**：

- `ValueError`：长度不一致：`"dot: a and b must have the same length"`
- dtype/连续性/ndim 错误同上

**示例**：

```python
import numpy as np
import rvv

a = np.arange(8, dtype=np.float32)
print(rvv.dot(a, a))
```

---

### 2.5 `rvv.norm_l2(a) -> float`

**功能**：L2 范数（欧几里得范数）。

- 定义：`sqrt(dot(a, a))`

**参数**：

- `a`：1-D float32 buffer

**返回**：

- Python `float`

**数值误差说明（重要）**：

`dot` 和 `norm` 都是“归约”运算（reduction）。
当向量很大时（例如 1e6 长度），由于不同实现的归约顺序不同（RVV 分块、标量循环、NumPy/BLAS 向量化等），最终结果可能与 NumPy 有**很小的相对误差**。

建议比较时使用相对误差（例如 `1e-4 ~ 1e-3`）而不是严格相等。

**示例**：

```python
import numpy as np
import rvv

a = np.random.randn(1000000).astype(np.float32)
print(rvv.norm_l2(a))
```

---

## 3. 矩阵运算 API（2-D）

### 3.1 `rvv.matmul(A, B) -> ndarray[float32]`

**功能**：矩阵乘法。

- 输入：
  - `A`：形状 `(m, k)`
  - `B`：形状 `(k, n)`
- 输出：
  - `C`：形状 `(m, n)`

**参数**：

- `A`：2-D float32 buffer（`ndim=2`，C-contiguous，行主序）
- `B`：2-D float32 buffer（`ndim=2`，C-contiguous，行主序）

**返回**：

- `C`：2-D float32 数组

**错误**：

- `ValueError`：
  - 维度不是 2：`"A must have ndim=2, got ndim=..."`
  - 形状不匹配：
    - `"matmul: shape mismatch: A is (m,k) but B is (k2,n)"`

**示例**：

```python
import numpy as np
import rvv

A = np.random.randn(2, 3).astype(np.float32)
B = np.random.randn(3, 4).astype(np.float32)
C = rvv.matmul(A, B)
print(C.shape)
```

---

## 4. 性能建议

- 确保输入是 **float32** 且 **C-contiguous**，避免不必要的复制。
- 大数组上，`add/sub/scale` 通常更容易看到 RVV 性能收益。
- `matmul` 是否快于 NumPy 取决于 NumPy 是否链接了高性能 BLAS（嵌入式环境中 NumPy 常常没有或性能有限）。

---

## 5. 常见错误与排查

### 5.1 `... must be float32-compatible buffer ...`

说明输入不是 float32。

解决：

```python
x = x.astype(np.float32, copy=False)
```

### 5.2 `... must be C-contiguous float32 buffer`

说明输入是切片/转置等非连续视图。

解决：

```python
x = np.ascontiguousarray(x, dtype=np.float32)
```

### 5.3 `add/sub/dot: a and b must have the same length`

说明向量长度不一致。

---

## 6. 与实现对应关系（供开发者）

- Python 绑定：`rvv_ext/main/src/bind_rvv.cpp`
- C++ 公共接口声明：`rvv_ext/main/include/rvv.hpp`
- RVV 0.7.1 实现：`rvv_ext/main/src/rvv_rvv071.cpp`（仅在 `__riscv_vector` 下编译）
- 标量实现：`rvv_ext/main/src/rvv_scalar.cpp`

---

## 7. 最小示例（组合使用）

```python
import numpy as np
import rvv

a = np.arange(8, dtype=np.float32)
b = np.arange(8, dtype=np.float32)

c = rvv.add(a, b)
d = rvv.sub(a, b)
e = rvv.scale(a, 2.0)

print(c)
print(d)
print(e)
print(rvv.dot(a, b))
print(rvv.norm_l2(a))

A = np.arange(6, dtype=np.float32).reshape(2, 3)
B = np.arange(12, dtype=np.float32).reshape(3, 4)
print(rvv.matmul(A, B))
```



# 以下是二次开发可以参考的
# rvv (SG2002/C906 RVV 加速的 NumPy 运算)

此文件夹包含一个小型的 C++/pybind11 Python 扩展，提供 **NumPy 兼容** 的向量/矩阵运算，并为 SG2002 (C906) 提供 **RVV 0.7.1** 快速路径。

> 目标 Python：**3.11.6**（对应 SDK 组件 `python3_lib_maixcam_musl_3.11.6`）。

---

## 你可能会遇到的几个关键点

- 一定要在项目根目录 `rvv_ext/` 执行构建，不要在 `rvv_ext/main/` 里执行。
  - 否则会生成 `rvv_ext/main/build/...` 的配置并导致输出看起来“无限循环”。
- 必须设置 SDK 环境变量：
  - `MY_SDK_PATH=/root/xmusic/Auto-bind-Python-from-CC--main/Auto-bind-Python-from-CC--main`
  - 不设置会报找不到 `/tools/cmds`。
- 交叉编译时 `TOOLCHAIN_PATH` **必须是绝对路径**，否则 CMake 会报：
  - `TOOLCHAIN_PATH set error: ...`
- `distclean` 会删除 `build/`，之后不能直接 `cmake --build build ...`，否则会报：
  - `Error: could not load cache`
  - 必须先重新执行 `python3 project.py build` 生成 `build/CMakeCache.txt`。
- 嵌入式 Linux 上通常 **无法编译/安装 NumPy**。本库 **wheel 安装不依赖 NumPy**（`install_requires=[]`）。
  - 但如果你要对比 NumPy 的结果/速度，需要目标环境能装 NumPy。
- `norm_l2` / `dot` 在超大向量（例如 1e6）上可能与 NumPy 有轻微差异（归约顺序导致浮点误差），应使用相对误差比较，而不是严格相等。

---

## 输入约束（与 NumPy 兼容的关键点）

本库的绑定实现位于 `main/src/bind_rvv.cpp`，核心行为如下：

- 所有运算都是 **float32-only**
- 输入接受：
  - NumPy 可用时：优先将输入转换为 **`float32 + C-contiguous`**（`py::array_t<float, c_style|forcecast>`）
    - 这意味着 `float64` 或非连续数组会发生 **复制/转换**（这是为了兼容性与稳定性）
  - NumPy 不可用时：走 **buffer protocol** 路径
    - 要求 buffer 的 `format == 'f'` 且 `itemsize == 4`
    - 要求 **严格 C-contiguous**（否则会抛 `ValueError`）

如果你希望“零拷贝”并获得最佳性能，建议在调用前确保：

```python
x = np.ascontiguousarray(x, dtype=np.float32)
```

---

## IDE 代码提示（自动补全/类型提示）

由于 `rvv` 是 **二进制扩展模块**（`rvv.so`），IDE 无法像纯 Python 一样从源码推断函数签名。
本项目已通过 **PEP 561** 的方式提供类型提示：

- `rvv_ext/rvv.pyi`：模块存根（stub），为 `add/sub/scale/dot/norm_l2/matmul` 提供签名与说明
- `rvv_ext/py.typed`：标记文件，告知工具/IDE “该包携带类型信息”

并且在打包 wheel 时会把它们一并打入 whl（见 `rvv_ext/setup.py`）。

### 方式 A：安装 wheel 后获得提示（推荐）但我懒得打包了

在目标机/开发机安装生成的 wheel 后，IDE 通常会自动读取 `.pyi`，为 `import rvv` 提供补全：

```bash
pip install --no-deps --force-reinstall dist/*.whl
```

### 方式 B：在源码目录直接开发时获得提示

如果你暂时不安装 wheel，而是在源码目录直接写代码：

- 确保 IDE 的解释器/项目索引能看到 `rvv_ext/rvv.pyi`
- 可在 PyCharm 中将 `rvv_ext/` 目录标记为 **Sources Root**（或加入 `PYTHONPATH`）

> 注意：无论哪种方式，运行时导入仍然是 `import rvv`。

---

## 主要目标

- 直接接受 **NumPy `ndarray` / buffer-protocol** 输入。
- 内部将输入转换为 **float32 + C连续** 缓冲区（内核期望的格式）。
- 当可用时使用 RVV（RISC-V 向量扩展）实现（`__riscv_vector`）。
- 提供标量回退，以便相同的源码可以在非 RISC-V 主机上构建/测试。

---

## Python API（概览）

顶层模块名为 `rvv`：

- `rvv.add(a, b) -> ndarray`
- `rvv.sub(a, b) -> ndarray`
- `rvv.scale(a, k) -> ndarray`
- `rvv.dot(a, b) -> float`
- `rvv.norm_l2(a) -> float`
- `rvv.matmul(A, B) -> ndarray`

更完整的 API 文档请见：`lib/rvvapi.md`。

---

## 构建模式选择：交叉编译（MaixCam） vs 主机测试（Linux）

项目在 `main/CMakeLists.txt` 中支持两类构建模式：

- **交叉编译到 SG2002（推荐）**：启用 `MaixCam`
  - 会启用 RVV ISA flags（如 `-march=rv64imafdcv0p7xthead`）
  - 会链接 SDK 的 `python3_lib_maixcam_musl_3.11.6` 头文件/库，避免 `Python.h` 缺失
- **主机 Linux 测试**：启用 `Linux`
  - 先尝试 system `Python.h`（`python3-dev`），找不到则回退到 SDK python 组件

> 经验：如果你看到 `fatal error: Python.h: No such file or directory`，说明当前构建模式没有拿到 Python 开发头。

---

## 使用 Auto-bind-Python-from-CC--main 构建 (Linux)

此项目使用与 `Auto-bind-Python-from-CC--main/examples/demo` 相同的构建系统。

### 0) 设置 SDK 环境变量（必须）

```bash
export MY_SDK_PATH=/root/xmusic/Auto-bind-Python-from-CC--main/Auto-bind-Python-from-CC--main
```

### 1) 打开 menuconfig

```bash
cd /root/xmusic/rvv_ext
python3 project.py menuconfig
```

### 2) 配置工具链（交叉编译到 SG2002）

- `-mcpu=c906fdv`
- `-march=rv64imafdcv0p7xthead`
- `-mcmodel=medany`
- `-mabi=lp64d`

#### 替代方案：不使用 menuconfig 进行配置

您也可以通过标志进行配置：

```bash
python3 project.py config \
  --toolchain /root/xmusic/host-tools/gcc/riscv64-linux-musl-x86_64/bin \
  --toolchain-prefix riscv64-unknown-linux-musl-
```

或者通过此项目顶级 `CMakeLists.txt` 使用的环境变量：

```bash
export MY_TOOLCHAIN_PATH=/root/xmusic/toolchains/maixcam/host-tools/gcc/riscv64-linux-musl-x86_64/bin
```

### 3) 构建 + wheel 包

```bash
python3 project.py build
```

产物：
- 编译的扩展：`build/main/libmain.so`
- Wheel 包：`dist/*.whl`

### 4) 快速 RVV 启用检查（可选）

在执行 `python3 project.py build` 后，检查构建日志中的编译命令行是否包含：

- `-march=rv64imafdcv0p7xthead`

如果存在该标志，`__riscv_vector` 应该被定义，RVV 实现（`rvv_rvv071.cpp`）将会被编译。

## Python API

顶层模块名为 `rvv`。
  `/root/xmusic/toolchains/maixcam/host-tools/gcc/riscv64-linux-musl-x86_64/bin`
  （请根据您实际的工作空间路径调整前缀 `/root/xmusic`）
- `CONFIG_TOOLCHAIN_PREFIX` =
  `riscv64-unknown-linux-musl-`

然后选择 RISCV64 目标（MaixCam）。

当启用 `MaixCam` 时，此项目的 `main/CMakeLists.txt` 已经注入了 SG2002 所需的 RVV 标志：

- `-mcpu=c906fdv`
- `-march=rv64imafdcv0p7xthead`
- `-mcmodel=medany`
- `-mabi=lp64d`

#### 替代方案：不使用 menuconfig 进行配置

您也可以通过标志进行配置：

```bash
python3 project.py config \
  --toolchain /root/xmusic/toolchains/maixcam/host-tools/gcc/riscv64-linux-musl-x86_64/bin \
  --toolchain-prefix riscv64-unknown-linux-musl-
```

或者通过此项目顶级 `CMakeLists.txt` 使用的环境变量：

```bash
export MY_TOOLCHAIN_PATH=/root/xmusic/toolchains/maixcam/host-tools/gcc/riscv64-linux-musl-x86_64/bin
```

### 3) 构建 + wheel 包

```bash
python3 project.py build
```

产物：
- 编译的扩展：`build/main/libmain.so`
- Wheel 包：`dist/*.whl`

### 4) 快速 RVV 启用检查（可选）

在执行 `python3 project.py build` 后，检查构建日志中的编译命令行是否包含：

- `-march=rv64imafdcv0p7xthead`

如果存在该标志，`__riscv_vector` 应该被定义，RVV 实现（`rvv_rvv071.cpp`）将会被编译。

## Python API

顶层模块名为 `rvv`。

- `rvv.add(a, b) -> ndarray`
- `rvv.sub(a, b) -> ndarray`
- `rvv.scale(a, k) -> ndarray`
- `rvv.dot(a, b) -> float`
- `rvv.norm_l2(a) -> float`
- `rvv.matmul(A, B) -> ndarray`

所有数组输入都会在内部转换为 `float32` 和 C 连续格式。

## 测试

## 测试

测试位于 `rvv_ext/tests` 目录，需要 NumPy + pytest。

```bash
python3 -c "import rvv; import numpy as np; a=np.arange(8,dtype=np.float32); print(rvv.add(a,a)); print(rvv.dot(a,a))"
```

---

## 测试与性能对比（不依赖 pytest）

运行：

```bash
python3 tests/test_rvv.py
```

### 运行 `cmake --build build ...` 时出现 "Error: could not load cache" 错误

当 CMake 缓存（`build/CMakeCache.txt`）缺失时会发生这种情况。
常见原因：
- 您运行了 `python3 project.py distclean` 然后**没有**重新运行 CMake 配置步骤。
- `build/` 目录被删除或为空。

解决方法：

```bash
cd /path/to/rvv_ext

# 重新运行配置（生成 build/CMakeCache.txt）
python3 project.py build

# 然后编译
cmake --build build --target main -- -j"$(nproc)"
```

### `setup.py` 显示 `Native library not found: build/main/libmain.so`

这意味着您还没有构建扩展（或者它被构建到了不同的文件夹中）。

检查：

当 CMake 缓存（`build/CMakeCache.txt`）缺失时会发生这种情况。
常见原因：
- 您运行了 `python3 project.py distclean` 然后**没有**重新运行 CMake 配置步骤。
- `build/` 目录被删除或为空。

解决方法：

```bash
cd /path/to/rvv_ext

# 重新运行配置（生成 build/CMakeCache.txt）
python3 project.py build

# 然后编译
cmake --build build --target main -- -j"$(nproc)"
```

### `setup.py` 显示 `Native library not found: build/main/libmain.so`

这意味着您还没有构建扩展（或者它被构建到了不同的文件夹中）。

检查：

```bash
find build -maxdepth 4 -name 'libmain.so' -o -name '*.so' | sort
```

如果 `libmain.so` 存在但不在 `build/main/` 下，请相应地调整 `setup.py` 中的 `SO_FILE_PATH`。

## 复制粘贴命令（嵌入式 Linux）

### A) 在当前机器上构建 wheel 包（安装时不需要 NumPy）

### A) 在当前机器上构建 wheel 包（安装时不需要 NumPy）

```bash
cd /home/ywj/ywj2/rvv_ext   # 根据您的实际路径调整

# (可选) 完全清理：这会移除 build/ 和 CMakeCache.txt
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

> 如果您只想清理编译的对象但保留 CMake 缓存，请优先使用：
>
> ```bash
> python3 project.py clean
> ```
>
> 而不是 `distclean`。
#### 替代方案：不使用 menuconfig 进行配置
>
> ```bash
> python3 project.py clean
> ```
>
> 而不是 `distclean`。
#### 替代方案：不使用 menuconfig 进行配置

您也可以通过标志进行配置：

```bash
python3 project.py config \
  --toolchain /root/xmusic/host-tools/gcc/riscv64-linux-musl-x86_64/bin \
  --toolchain-prefix riscv64-unknown-linux-musl-
```

或者通过此项目顶级 `CMakeLists.txt` 使用的环境变量：

```bash
export MY_TOOLCHAIN_PATH=/root/xmusic/toolchains/maixcam/host-tools/gcc/riscv64-linux-musl-x86_64/bin
```

### 3) 构建 + wheel 包

```bash
export MY_TOOLCHAIN_PATH=/root/xmusic/toolchains/maixcam/host-tools/gcc/riscv64-linux-musl-x86_64/bin
```

### 3) 构建 + wheel 包

```bash
python3 project.py build
```

产物：
- 编译的扩展：`build/main/libmain.so`
- Wheel 包：`dist/*.whl`

### 4) 快速 RVV 启用检查（可选）

在执行 `python3 project.py build` 后，检查构建日志中的编译命令行是否包含：

- `-march=rv64imafdcv0p7xthead`

如果存在该标志，`__riscv_vector` 应该被定义，RVV 实现（`rvv_rvv071.cpp`）将会被编译。

## Python API

在执行 `python3 project.py build` 后，检查构建日志中的编译命令行是否包含：

- `-march=rv64imafdcv0p7xthead`

如果存在该标志，`__riscv_vector` 应该被定义，RVV 实现（`rvv_rvv071.cpp`）将会被编译。

## Python API

顶层模块名为 `rvv`。

- `rvv.add(a, b) -> ndarray`
- `rvv.sub(a, b) -> ndarray`
- `rvv.scale(a, k) -> ndarray`
- `rvv.dot(a, b) -> float`
- `rvv.norm_l2(a) -> float`
- `rvv.matmul(A, B) -> ndarray`
- `rvv.sub(a, b) -> ndarray`
- `rvv.scale(a, k) -> ndarray`
- `rvv.dot(a, b) -> float`
- `rvv.norm_l2(a) -> float`
- `rvv.matmul(A, B) -> ndarray`

所有数组输入都会在内部转换为 `float32` 和 C 连续格式。

## 测试

测试位于 `rvv_ext/tests` 目录，需要 NumPy + pytest。

## 测试

测试位于 `rvv_ext/tests` 目录，需要 NumPy + pytest。

```bash
pytest -q
```

在 SG2002 上，您还可以运行微基准测试：

```bash
python3 tests/bench_perf.py
```

## 故障排除

### 运行 `cmake --build build ...` 时出现 "Error: could not load cache" 错误

当 CMake 缓存（`build/CMakeCache.txt`）缺失时会发生这种情况。
常见原因：
- 您运行了 `python3 project.py distclean` 然后**没有**重新运行 CMake 配置步骤。
- `build/` 目录被删除或为空。
常见原因：
- 您运行了 `python3 project.py distclean` 然后**没有**重新运行 CMake 配置步骤。
- `build/` 目录被删除或为空。

解决方法：

```bash
cd /path/to/rvv_ext

# Re-run configure (generates build/CMakeCache.txt)
python3 project.py build
python3 project.py build

# Then compile
cmake --build build --target main -- -j"$(nproc)"
cmake --build build --target main -- -j"$(nproc)"
```

### `setup.py` 显示 `Native library not found: build/main/libmain.so`

这意味着您还没有构建扩展（或者它被构建到了不同的文件夹中）。

检查：

```bash
find build -maxdepth 4 -name 'libmain.so' -o -name '*.so' | sort
```

如果 `libmain.so` 存在但不在 `build/main/` 下，请相应地调整 `setup.py` 中的 `SO_FILE_PATH`。

## 复制粘贴命令（嵌入式 Linux）

### A) 在当前机器上构建 wheel 包（安装时不需要 NumPy）

```bash
cd /home/ywj/ywj2/rvv_ext   # adjust to your real path

# (Optional) full clean: this removes build/ and CMakeCache.txt
python3 project.py distclean
python3 project.py distclean

# 1) Configure CMake (re-creates build/ and build/CMakeCache.txt)
python3 project.py build

# 健全性检查（配置后应该存在）
ls -la build/CMakeCache.txt

# 2) Compile the extension shared library (creates build/main/libmain.so)
cmake --build build --target main -- -j"$(nproc)"

# Sanity check (should exist after compile)
ls -la build/main/libmain.so

# 3) Build wheel (creates dist/*.whl)
python3 setup.py bdist_wheel

# 4) List wheel
ls -la build/CMakeCache.txt

# 2) Compile the extension shared library (creates build/main/libmain.so)
cmake --build build --target main -- -j"$(nproc)"

# Sanity check (should exist after compile)
ls -la build/main/libmain.so

# 3) Build wheel (creates dist/*.whl)
python3 setup.py bdist_wheel

# 4) List wheel
ls -la dist
```

> 如果您只想清理编译的对象但保留 CMake 缓存，请优先使用：
>
> ```bash
> python3 project.py clean
> ```
>
> 而不是 `distclean`。

> 如果您只想清理编译的对象但保留 CMake 缓存，请优先使用：
>
> ```bash
> python3 project.py clean
> ```
>
> 而不是 `distclean`。
