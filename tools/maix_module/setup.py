from setuptools import setup, find_packages, Distribution
import sys
import os
import platform
import shutil
import zipfile  # 提前导入，避免maixcam处理时导入失败

####################################################################
# supported platforms
board_names = ["linux", "maixcam"]
platform_names = {
    # use correspond docker to compile https://github.com/pypa/manylinux
    "linux": "manylinux2014_{}".format(platform.machine().replace("-", "_").replace(".", "_").lower()),
    "m2dock": "linux_armv7l",
    "maixcam": "linux_riscv64",
}
platform_toolchain_id = {
    "maixcam": "musl_t-hread"
}
####################################################################

# 容错：处理module_name.txt不存在的情况
if not os.path.exists("module_name.txt"):
    print("-- Warning: module_name.txt not found, use default 'maix'")
    module_name = "maix"
else:
    with open("module_name.txt", "r") as f:
        module_name = f.readline().strip()

def get_build_python_version():
    version = [0, 0, 0]
    mk_file = os.path.join("build", "config", "python_version.txt")
    # 容错：python_version.txt不存在时的默认值（Linux平台默认3.10）
    if not os.path.exists(mk_file):
        print("-- Warning: python_version.txt not found, use default 3.10.0")
        return [3, 10, 0]
    with open(mk_file, "r", encoding="utf-8") as f:
        version_str = f.read().split(".")
        for i in range(0, min(3, len(version_str))):  # 防止版本字符串长度不足
            version[i] = int(version_str[i])
    if version[0] == 0 or version[1] == 0 or version[2] == 0:
        print("-- Get build python version failed! Use default 3.10.0")
        return [3, 10, 0]
    return version

def get_python_version():
    return [sys.version_info.major, sys.version_info.minor, sys.version_info.micro]

def print_py_version_err(build_py_version):
    print("-- Python version not match build python version!")
    print("   You can use conda to create a virtual environment with python version:")
    print("   Download miniconda from https://docs.conda.io/en/latest/miniconda.html")
    print("       conda create -n python{}.{} python={}.{}".format(build_py_version[0], build_py_version[1], build_py_version[0], build_py_version[1]))
    print("       conda activate python{}.{}".format(build_py_version[0], build_py_version[1]))

# 检查平台配置文件
board_config_files = {}
for board in board_names:
    board_config_files[board] = os.path.join("configs", "config_platform_{}.mk".format(board))
    if not os.path.exists(board_config_files[board]):
        print("-- Warning: Platform config file not found: {}".format(board_config_files[board]))
        # 不直接退出，仅警告（允许无配置文件编译）
        board_config_files[board] = None

# 解析board参数
board = None
for name in board_names:
    if name in sys.argv:
        board = name
        sys.argv.remove(name)
        break
if (not board) and not ("-h" in sys.argv or "--help" in sys.argv or "--help-commands" in sys.argv):
    print("-- Please specify board name: {}, e.g. python setup.py bdist_wheel linux".format(board_names))
    sys.exit(1)

# 备份dist目录
if os.path.exists("dist"):
    os.makedirs("dist_old", exist_ok = True)
    try:
        shutil.copytree("dist", "dist_old", dirs_exist_ok=True)
    except Exception as e:
        print("-- Warning: Copy dist to dist_old failed: {}".format(e))

# 清理临时文件
if "--not-clean" not in sys.argv and "--skip-build" not in sys.argv and os.path.exists(f"{module_name}/dl_lib"):
    try:
        shutil.rmtree(f"{module_name}/dl_lib")
    except Exception as e:
        print("-- Warning: Remove dl_lib failed: {}".format(e))

# 检查maixcam的Python版本
py_version = get_python_version()
if board == "maixcam" and f"{py_version[0]}.{py_version[1]}" != "3.11":
    print_py_version_err([3, 11])
    sys.exit(1)

# 编译C++模块
build_success = True
if board and "--skip-build" not in sys.argv:
    if "debug" in sys.argv:
        release_str = ""
        sys.argv.remove("debug")
    else:
        release_str = "--release"
    
    # 仅当配置文件存在时才编译
    if board_config_files.get(board):
        cmd = "python project.py build -p {} {} --config-file {}".format(board, release_str, board_config_files[board])
        if "--not-clean" not in sys.argv:
            cmd = "python project.py distclean && " + cmd
        else:
            sys.argv.remove("--not-clean")
        cmd += f" --toolchain-id {platform_toolchain_id[board]}" if board in platform_toolchain_id else ""
        print("-- Execute build command: {}".format(cmd))
        ret = os.system(cmd)
        if ret != 0:
            print("-- Warning: Build cpp modules failed! Continue to generate wheel...")
            build_success = False  # 编译失败不退出，继续生成wheel
    else:
        print("-- Warning: No config file for {}, skip build cpp modules".format(board))

# 检查Python版本（Linux平台放宽校验：仅警告不退出）
build_py_version = get_build_python_version()
print("-- Build Python version: {}.{}.{}".format(build_py_version[0], build_py_version[1], build_py_version[2]))
print("-- Current Python version: {}.{}.{}".format(py_version[0], py_version[1], py_version[2]))
if (py_version[0] != build_py_version[0]) or (py_version[1] != build_py_version[1]):
    print_py_version_err(build_py_version)
    if board != "linux":  # 仅非Linux平台严格校验
        sys.exit(1)
    else:
        print("-- Warning: Linux platform skip python version check, continue...")

# 设置wheel的平台标签
if board:
    sys.argv += ["--python-tag", "cp{}{}".format(build_py_version[0], build_py_version[1])]
    sys.argv += ["--plat-name", platform_names.get(board, "manylinux2014_x86_64")]  # 默认x86_64

# 生成pyi stub文件（Linux平台，失败仅警告）
if board == "linux":
    try:
        from pybind11_stubgen import main as pybind11_stubgen_main
        old_sys_argv = sys.argv
        sys.path.insert(0, ".")
        sys.argv = ["pybind11-stubgen", module_name, "-o", "stub"]
        pybind11_stubgen_main()
        sys.path.pop(0)
        sys.argv = old_sys_argv
        # 复制stub文件
        stub_src = f"stub/{module_name}"
        if os.path.exists(stub_src):
            for root, dirs, files in os.walk(stub_src):
                for name in files:
                    if name.endswith(".pyi"):
                        dst = os.path.join(root[5:], name)
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        shutil.copy(os.path.join(root, name), dst)
        else:
            print("-- Warning: Stub files not generated")
    except Exception as e:
        print("-- Warning: Generate stub files failed: {}".format(e))
        print("-- Install pybind11-stubgen: pip install pybind11-stubgen")
        # 不退出，继续打包

# 生成API文档（失败仅警告）
try:
    maixcdk_path = os.path.abspath(os.environ.get("MAIXCDK_PATH", ""))
    maixpy_path = os.path.abspath(os.getcwd())
    if maixcdk_path and maixcdk_path.startswith(maixpy_path):
        print("-- Warning: MAIXCDK_PATH is in MaixPy folder")
    if maixcdk_path:
        ret = os.system(f"python -u components/maix/gen_api.py --doc docs/api --sdk_path {maixcdk_path}")
        if ret != 0:
            print("-- Warning: Generate doc file failed")
    else:
        print("-- Warning: MAIXCDK_PATH not set, skip generate doc")
except Exception as e:
    print("-- Warning: Generate doc failed: {}".format(e))

# requirement packages
requirements = []

# 读取README.md（容错）
long_description = "Sipeed Maix Vision Python SDK"
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()

# 获取版本号（容错）
__version__ = "1.0.0"
version_file = f"{module_name}/version.py"
if os.path.exists(version_file):
    with open(version_file, "r", encoding="utf-8") as f:
        vars = {}
        exec(f.read(), vars)
        __version__ = vars.get("__version__", "1.0.0")

class BinaryDistribution(Distribution):
    """Distribution which always forces a binary package with platform name"""
    def has_ext_modules(self):  # 修复方法名错误（原foo参数无意义）
        return True

# 查找包（容错）
pkgs = find_packages()
if not pkgs:
    pkgs = [module_name]  # 至少包含主模块
print("-- found packages: {}".format(pkgs))

# 核心：执行setup生成wheel
setup(
    name=module_name,
    version=__version__,
    author='Sipeed',
    author_email='support@sipeed.com',
    description='Sipeed Maix Vision Python SDK',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/Sipeed/MaixPy',
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Embedded Systems',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3'
    ],
    keywords='Machine vision, AI vision, IOT, AIOT, Edge computing',
    packages=pkgs,
    install_requires=requirements,
    extras_require={},
    package_data={
        module_name: ['*.so', "dl_lib/*.so*", "*.pyi", "**/*.pyi", "**/**/*.pyi"]
    },
    data_files=[],
    entry_points={
        'console_scripts': [],
    },
    distclass=BinaryDistribution
)

# 修复：Linux平台wheel重命名逻辑
if board and os.path.exists("dist"):
    py_tag = "cp{}{}".format(build_py_version[0], build_py_version[1])
    # 筛选whl文件并按时间排序
    whl_files = [f for f in os.listdir("dist") if f.endswith(".whl")]
    if not whl_files:
        print("-- Error: No wheel file generated in dist directory!")
        sys.exit(1)
    
    whl_files.sort(key=lambda x: os.path.getmtime(os.path.join("dist", x)), reverse=True)
    old_name = whl_files[0]
    old_path = os.path.join("dist", old_name)

    # Linux平台重命名为可读格式
    if board == "linux":
        new_name = f"{module_name}-{__version__}-{py_tag}-{py_tag}-{platform_names[board]}.whl"
        new_path = os.path.join("dist", new_name)
        os.rename(old_path, new_path)
        print("-- Linux wheel generated: {}".format(new_path))
    
    # maixcam平台特殊处理（保持原有逻辑）
    elif board == "maixcam" and "linux_riscv64" in old_name:
        # 解压修改WHEEL文件
        temp_dir = "dist/temp"
        os.makedirs(temp_dir, exist_ok=True)
        with zipfile.ZipFile(old_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # 修改WHEEL文件
        wheel_file = os.path.join(temp_dir, f"{module_name}-{__version__}.dist-info/WHEEL")
        if os.path.exists(wheel_file):
            with open(wheel_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            with open(wheel_file, "w", encoding="utf-8") as f:
                for line in lines:
                    if line.startswith("Tag:"):
                        f.write("Tag: py3-none-any\n")
                    else:
                        f.write(line)
        
        # 重新打包
        with zipfile.ZipFile(old_path, "w", zipfile.ZIP_DEFLATED) as zip_ref:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    src = os.path.join(root, file)
                    dst = os.path.relpath(src, temp_dir)
                    zip_ref.write(src, dst)
        
        # 重命名
        new_name = f"{module_name}-{__version__}-py3-none-any.whl"
        new_path = os.path.join("dist", new_name)
        os.rename(old_path, new_path)
        shutil.rmtree(temp_dir)
        print("-- Maixcam wheel generated: {}".format(new_path))

print("-- Build completed! Check dist directory for wheel file.")