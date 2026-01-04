import os
import sys

def main():
    # ===================== 1. Read and validate module name =====================
    try:
        with open("module_name.txt", "r", encoding="utf-8") as f:
            module_name = f.readline().strip()
    except FileNotFoundError:
        raise Exception("Error: module_name.txt file not found. Please create it first and fill in the module name (e.g., maix_kkk)")
    except Exception as e:
        raise Exception(f"Failed to read module_name.txt: {e}")

    # Validate module name must start with maix_
    if not module_name.startswith("maix_"):
        raise Exception("Error: Module name must start with 'maix_' (e.g., maix_kkk)")

    # Optional: Specify initial version number from command line (Example: python init_files.py 1.0.1)
    init_version = sys.argv[1] if len(sys.argv) > 1 else "1.0.0"
    try:
        version_major, version_minor, version_patch = init_version.split(".")
        # Verify version number is numeric
        int(version_major), int(version_minor), int(version_patch)
    except ValueError:
        raise Exception(f"Error: Invalid version number format (Please use format like 1.0.0, current: {init_version})")

    # ===================== 2. Generate test file (test/test_import.py) =====================
    def write_test_import_file():
        test_file = "test/test_import.py"
        if os.path.exists(test_file):
            print(f"Note: {test_file} already exists, skip generation")
            return
        try:
            os.makedirs("test", exist_ok=True)
            content = f"import {module_name}\nprint(f'Successfully imported module: {module_name}')"
            with open(test_file, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Successfully generated: {test_file}")
        except PermissionError:
            raise Exception(f"Error: Insufficient permissions to create {test_file}")
        except Exception as e:
            raise Exception(f"Failed to generate test file: {e}")

    # ===================== 3. Generate core module files (__init__.py / version.py) =====================
    def write_module_dir():
        # Generate __init__.py content (Fix hardcoded extension module name)
        init_content = f'''from .version import __version__
from ._{module_name} import *
'''
        # Generate version.py content (Dynamic version number)
        version_content = f'''# Versions should comply with PEP440: https://peps.python.org/pep-0440/

version_major = {version_major}
version_minor = {version_minor}
version_patch = {version_patch}

__version__ = "{version_major}.{version_minor}.{version_patch}"
'''
        try:
            # Create module directory
            os.makedirs(module_name, exist_ok=True)

            # Generate __init__.py
            init_file = f"{module_name}/__init__.py"
            if not os.path.exists(init_file):
                with open(init_file, "w", encoding="utf-8") as f:
                    f.write(init_content)
                print(f"Successfully generated: {init_file}")
            else:
                print(f"Note: {init_file} already exists, skip generation")

            # Generate version.py
            version_file = f"{module_name}/version.py"
            if not os.path.exists(version_file):
                with open(version_file, "w", encoding="utf-8") as f:
                    f.write(version_content)
                print(f"Successfully generated: {version_file}")
            else:
                print(f"Note: {version_file} already exists, skip generation")
        except PermissionError:
            raise Exception(f"Error: Insufficient permissions to create {module_name} directory/files")
        except Exception as e:
            raise Exception(f"Failed to generate core module files: {e}")

    # ===================== 4. Generate C++ extension module files (hpp/cpp) =====================
    def write_component_dir():
        # Generate .hpp header file content
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
        # Generate .cpp source file content
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
            # Create directories
            include_dir = "components/maix/include"
            src_dir = "components/maix/src"
            os.makedirs(include_dir, exist_ok=True)
            os.makedirs(src_dir, exist_ok=True)

            # Generate .hpp file
            hpp_file = f"{include_dir}/{module_name}.hpp"
            if not os.path.exists(hpp_file):
                with open(hpp_file, "w", encoding="utf-8") as f:
                    f.write(hpp_content)
                print(f"Successfully generated: {hpp_file}")
            else:
                print(f"Note: {hpp_file} already exists, skip generation")

            # Generate .cpp file
            cpp_file = f"{src_dir}/{module_name}.cpp"
            if not os.path.exists(cpp_file):
                with open(cpp_file, "w", encoding="utf-8") as f:
                    f.write(cpp_content)
                print(f"Successfully generated: {cpp_file}")
            else:
                print(f"Note: {cpp_file} already exists, skip generation")
        except PermissionError:
            raise Exception("Error: Insufficient permissions to create components directory/files")
        except Exception as e:
            raise Exception(f"Failed to generate C++ extension files: {e}")

    # ===================== 5. Generate README documentation =====================
    def write_readme_files():
        # English README
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
            print(f"Successfully generated: {readme_en}")
        else:
            print(f"Note: {readme_en} already exists, skip generation")

        # Chinese README (renamed to README_CN.md for consistency)
        readme_cn = "README_CN.md"
        if not os.path.exists(readme_cn):
            cn_content = f"""# MaixPy Module: {module_name}

## Quick Start
1. Compile module: `python setup.py bdist_wheel 'platform'`
2. Install module: `pip install dist/{module_name}*.whl`
3. Test import: `python test/test_import.py`

## Development Guide
- Python module root directory: `{module_name}/`
- C++ source file: `components/maix/src/{module_name}.cpp`
- C++ header file: `components/maix/include/{module_name}.hpp`
- Version management file: `{module_name}/version.py`

## TODO
- Add detailed API documentation
- Add unit tests for core functions
"""
            with open(readme_cn, "w", encoding="utf-8") as f:
                f.write(cn_content)
            print(f"Successfully generated: {readme_cn}")
        else:
            print(f"Note: {readme_cn} already exists, skip generation")

    # ===================== Execute all generation logic =====================
    write_test_import_file()
    write_module_dir()
    write_component_dir()
    write_readme_files()

    print(f"\n✅ Module project skeleton generation completed! Module name: {module_name}")
    print(f"📌 Next steps:")
    print(f"   1. Modify {module_name}/__init__.py to add custom interfaces")
    print(f"   2. Improve components/maix/src/{module_name}.cpp to implement business logic")
    print(f"   3. Execute python setup.py bdist_wheel 'platform' to compile the module")
    print(f"   4. Modify whl package version: in {module_name}/version.py file")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Generation failed: {e}")
        sys.exit(1)