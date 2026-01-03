import os
import sys

def main():
    # ===================== 1. 读取并校验模块名 =====================
    try:
        with open("module_name.txt", "r", encoding="utf-8") as f:
            module_name = f.readline().strip()
    except FileNotFoundError:
        raise Exception("错误：未找到 module_name.txt 文件，请先创建并填写模块名（如 maix_kkk）")
    except Exception as e:
        raise Exception(f"读取 module_name.txt 失败：{e}")

    # 校验模块名必须以 maix_ 开头
    if not module_name.startswith("maix_"):
        raise Exception("错误：模块名必须以 'maix_' 开头（如 maix_kkk）")

    # 可选：从命令行指定初始版本号（示例：python generate_module.py 1.0.1）
    init_version = sys.argv[1] if len(sys.argv) > 1 else "1.0.0"
    try:
        version_major, version_minor, version_patch = init_version.split(".")
        # 验证版本号为数字
        int(version_major), int(version_minor), int(version_patch)
    except ValueError:
        raise Exception(f"错误：版本号格式无效（请传入如 1.0.0 的格式，当前：{init_version}）")

    # ===================== 2. 生成测试文件（test/test_import.py） =====================
    def write_test_import_file():
        test_file = "test/test_import.py"
        if os.path.exists(test_file):
            print(f"提示：{test_file} 已存在，跳过生成")
            return
        try:
            os.makedirs("test", exist_ok=True)
            content = f"import {module_name}\nprint(f'成功导入模块：{module_name}')"
            with open(test_file, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"成功生成：{test_file}")
        except PermissionError:
            raise Exception(f"错误：权限不足，无法创建 {test_file}")
        except Exception as e:
            raise Exception(f"生成测试文件失败：{e}")

    # ===================== 3. 生成模块核心文件（__init__.py / version.py） =====================
    def write_module_dir():
        # 生成 __init__.py 内容（修复硬编码扩展模块名）
        init_content = f'''from .version import __version__
from ._{module_name} import *
'''
        # 生成 version.py 内容（动态版本号）
        version_content = f'''# Versions should comply with PEP440: https://peps.python.org/pep-0440/

version_major = {version_major}
version_minor = {version_minor}
version_patch = {version_patch}

__version__ = "{version_major}.{version_minor}.{version_patch}"
'''
        try:
            # 创建模块目录
            os.makedirs(module_name, exist_ok=True)

            # 生成 __init__.py
            init_file = f"{module_name}/__init__.py"
            if not os.path.exists(init_file):
                with open(init_file, "w", encoding="utf-8") as f:
                    f.write(init_content)
                print(f"成功生成：{init_file}")
            else:
                print(f"提示：{init_file} 已存在，跳过生成")

            # 生成 version.py
            version_file = f"{module_name}/version.py"
            if not os.path.exists(version_file):
                with open(version_file, "w", encoding="utf-8") as f:
                    f.write(version_content)
                print(f"成功生成：{version_file}")
            else:
                print(f"提示：{version_file} 已存在，跳过生成")
        except PermissionError:
            raise Exception(f"错误：权限不足，无法创建 {module_name} 目录/文件")
        except Exception as e:
            raise Exception(f"生成模块核心文件失败：{e}")

    # ===================== 4. 生成 C++ 扩展模块文件（hpp/cpp） =====================
    def write_component_dir():
        # 生成 .hpp 头文件内容
        hpp_content = f'''
#include "maix_basic.hpp"

namespace {module_name}::basic
{{
    /**
      * hello
      * @param name Name to say hello
      * @{module_name} {module_name}.basic.hello
      */
      void hello(const std::string &name);

}} // namespace {module_name}
'''
        # 生成 .cpp 源文件内容
        cpp_content = f'''#include "{module_name}.hpp"

namespace {module_name}::basic
{{
    void hello(const std::string &name)
    {{
        maix::log::info(("hello: " + name).c_str());
    }}
}} // namespace {module_name}
'''
        try:
            # 创建目录
            include_dir = "components/maix/include"
            src_dir = "components/maix/src"
            os.makedirs(include_dir, exist_ok=True)
            os.makedirs(src_dir, exist_ok=True)

            # 生成 .hpp 文件
            hpp_file = f"{include_dir}/{module_name}.hpp"
            if not os.path.exists(hpp_file):
                with open(hpp_file, "w", encoding="utf-8") as f:
                    f.write(hpp_content)
                print(f"成功生成：{hpp_file}")
            else:
                print(f"提示：{hpp_file} 已存在，跳过生成")

            # 生成 .cpp 文件
            cpp_file = f"{src_dir}/{module_name}.cpp"
            if not os.path.exists(cpp_file):
                with open(cpp_file, "w", encoding="utf-8") as f:
                    f.write(cpp_content)
                print(f"成功生成：{cpp_file}")
            else:
                print(f"提示：{cpp_file} 已存在，跳过生成")
        except PermissionError:
            raise Exception("错误：权限不足，无法创建 components 目录/文件")
        except Exception as e:
            raise Exception(f"生成 C++ 扩展文件失败：{e}")

    # ===================== 5. 生成 README 文档 =====================
    def write_readme_files():
        # 英文 README
        readme_en = "README.md"
        if not os.path.exists(readme_en):
            en_content = f"""# MaixPy Module: {module_name}

## Quick Start
1. Compile module: `python setup.py bdist_wheel maixcam`
2. Install module: `pip install dist/{module_name}*.whl`
3. Test import: `python test/test_import.py`

## Development Guide
- Python module root: `{module_name}/`
- C++ source code: `components/maix/src/{module_name}.cpp`
- C++ header file: `components/maix/include/{module_name}.hpp`
- Version management: `{module_name}/version.py`

## TODO
- Add detailed API documentation
- Add unit tests for core functions
"""
            with open(readme_en, "w", encoding="utf-8") as f:
                f.write(en_content)
            print(f"成功生成：{readme_en}")
        else:
            print(f"提示：{readme_en} 已存在，跳过生成")

        # 中文 README
        readme_zh = "README_ZH.md"
        if not os.path.exists(readme_zh):
            zh_content = f"""# MaixPy 模块：{module_name}

## 快速开始
1. 编译模块：`python setup.py bdist_wheel '平台'`
2. 安装模块：`pip install dist/{module_name}*.whl`
3. 测试导入：`python test/test_import.py`

## 开发指引
- Python 模块根目录：`{module_name}/`
- C++ 源码文件：`components/maix/src/{module_name}.cpp`
- C++ 头文件：`components/maix/include/{module_name}.hpp`
- 版本管理文件：`{module_name}/version.py`

## 待办事项
- 补充详细的 API 文档
- 为核心功能添加单元测试
"""
            with open(readme_zh, "w", encoding="utf-8") as f:
                f.write(zh_content)
            print(f"成功生成：{readme_zh}")
        else:
            print(f"提示：{readme_zh} 已存在，跳过生成")

    # ===================== 执行所有生成逻辑 =====================
    write_test_import_file()
    write_module_dir()
    write_component_dir()
    write_readme_files()

    print(f"\n✅ 模块工程骨架生成完成！模块名：{module_name}")
    print(f"📌 后续步骤：")
    print(f"   1. 修改 {module_name}/__init__.py 补充自定义接口")
    print(f"   2. 完善 components/maix/src/{module_name}.cpp 实现业务逻辑")
    print(f"   3. 执行 python setup.py bdist_wheel '平台' 编译模块")
    print(f"   4. whl包版本修改:{module_name}/version.py 文件内")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ 生成失败：{e}")
        sys.exit(1)