import os

with open("module_name.txt", "r") as f:
    module_name = f.readline().strip()

if not module_name.startswith("maix_"):
    raise Exception("module name must starts with maix_")


# Create test dir, and test_import.py
def write_test_dir():
    if os.path.exists("test/test_import.py"):
        return
    content = f"import {module_name}"
    os.makedirs("test", exist_ok=True)
    with open("test/test_import.py", "w", encoding="utf-8") as f:
        f.write(content)
write_test_dir()

# Create maix_xxx dir, write __init__.py and version.py
def write_module_dir():
    init_content = f'''from .version import __version__
from ._maix_xxx import *
'''
    version_content = '''# Versions should comply with PEP440: https://peps.python.org/pep-0440/

version_major = 1
version_minor = 0
version_patch = 0

__version__ = "{}.{}.{}".format(version_major, version_minor, version_patch)
'''
    os.makedirs(module_name, exist_ok=True)
    if not os.path.exists(f"{module_name}/__init__.py"):
        with open(f"{module_name}/__init__.py", "w", encoding="utf-8") as f:
            f.write(init_content)
    if not os.path.exists(f"{module_name}/version.py"):
        with open(f"{module_name}/version.py", "w", encoding="utf-8") as f:
            f.write(version_content)
write_module_dir()


# Create compent dir and files
def write_component_dir():
    cpp_content = f'''#include "{module_name}.hpp"

namespace {module_name}::basic
{{
    void hello(const std::string &name)
    {{
        maix::log::info(("hello: " + name).c_str());
    }}
}} // namespace {module_name}
'''
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
    os.makedirs("components/maix/include", exist_ok=True)
    os.makedirs("components/maix/src", exist_ok=True)
    if not os.path.exists(f"components/maix/include/{module_name}.hpp"):
        with open(f"components/maix/include/{module_name}.hpp", "w", encoding="utf-8") as f:
            f.write(hpp_content)
    if not os.path.exists(f"components/maix/src/{module_name}.cpp"):
        with open(f"components/maix/src/{module_name}.cpp", "w", encoding="utf-8") as f:
            f.write(cpp_content)
write_component_dir()

# Create readme
def write_test_dir():
    if os.path.exists("README.md"):
        return
    content = f"MaixPy module {module_name}\n====\n\nTODO: Add readme\n"
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)
    content = f"MaixPy 模块 {module_name}\n====\n\nTODO: 增加 readme\n"
    with open("README_ZH.md", "w", encoding="utf-8") as f:
        f.write(content)
write_test_dir()

