from setuptools import setup, find_packages, Distribution
import sys
import os
import platform
import shutil

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

def get_build_python_version():
    version = [0, 0, 0]
    mk_file = os.path.join("build", "config", "python_version.txt")
    with open(mk_file, "r", encoding="utf-8") as f:
        version_str = f.read().split(".")
        for i in range(0, 3):
            version[i] = int(version_str[i])
    if version[0] == 0 or version[1] == 0 or version[2] == 0:
        print("-- Get build python version failed!")
        sys.exit(1)
    return version

def get_python_version():
    return [sys.version_info.major, sys.version_info.minor, sys.version_info.micro]

board_config_files = {}
for board in board_names:
    board_config_files[board] = os.path.join("configs", "config_platform_{}.mk".format(board))
    if not os.path.exists(board_config_files[board]):
        print("-- Platform config file not found: {}".format(board_config_files[board]))
        sys.exit(1)

board = None
for name in board_names:
    if name in sys.argv:
        board = name
        sys.argv.remove(name)
        break
if (not board) and not ("-h" in sys.argv or "--help" in sys.argv or "--help-commands" in sys.argv):
    print("-- Please specify board name: {}, e.g. python setup.py bdist_wheel linux".format(board_names))
    sys.exit(1)

# copy dist to dist_old
if os.path.exists("dist"):
    os.makedirs("dist_old", exist_ok = True)
    shutil.copytree("dist", "dist_old", dirs_exist_ok=True)

# delete temp files
if "--not-clean" not in sys.argv and "--skip-build" not in sys.argv and os.path.exists("maix/dl_lib"):
    shutil.rmtree("maix/dl_lib")

def print_py_version_err(build_py_version):
    print("-- Python version not match build python version!")
    print("   You can use conda to create a virtual environment with python version:")
    print("   Download miniconda from https://docs.conda.io/en/latest/miniconda.html")
    print("       conda create -n python{}.{} python={}.{}".format(build_py_version[0], build_py_version[1], build_py_version[0], build_py_version[1]))
    print("       conda activate python{}.{}".format(build_py_version[0], build_py_version[1]))

# specially check for maixcam
py_version = get_python_version()
if board == "maixcam" and f"{py_version[0]}.{py_version[1]}" != "3.11":
    print_py_version_err([3, 11])
    sys.exit(1)

if board:
    # build CPP modules, and copy to build/lib/
    if "--skip-build" not in sys.argv:
        if "debug" in sys.argv:
            release_str = ""
            sys.argv.remove("debug")
        else:
            release_str = "--release"
        cmd = "python project.py build -p {} {} --config-file {}".format(board, release_str, board_config_files[board])
        if "--not-clean" not in sys.argv:
            cmd = "python project.py distclean && " + cmd
        else:
            sys.argv.remove("--not-clean")
        cmd += f" --toolchain-id {platform_toolchain_id[board]}" if board in platform_toolchain_id else ""
        ret = os.system(cmd)
        if ret != 0:
            print("-- Build cpp modules failed!")
            sys.exit(1)

# check python version
build_py_version = get_build_python_version()
print("-- Build Python version: {}.{}.{}".format(build_py_version[0], build_py_version[1], build_py_version[2]))
print("-- Python version: {}.{}.{}".format(py_version[0], py_version[1], py_version[2]))
if (py_version[0] != build_py_version[0]) or (py_version[1] != build_py_version[1]):
    print_py_version_err(build_py_version)
    sys.exit(1)

if board:
    # specific platform name for wheel package
    sys.argv += ["--python-tag", "cp{}{}".format(build_py_version[0], build_py_version[1])]
    # if board in  ["linux"]:
    sys.argv += ["--plat-name", platform_names[board]]

# generate pyi stub files
if board == "linux":
    try:
        from pybind11_stubgen import main as pybind11_stubgen_main
    except:
        print("-- Please install pybind11-stubgen first: pip install pybind11-stubgen")
        sys.exit(1)
    old_sys_argv = sys.argv
    sys.path.insert(0, ".") # to ensure use this folder's maix module but not system's
    sys.argv = ["pybind11-stubgen", "maix", "-o", "stub"]
    pybind11_stubgen_main()
    sys.path.pop(0)
    sys.argv = old_sys_argv
    # copy stub/maix/* to maix/ recursively
    for root, dirs, files in os.walk("stub/maix"):
        for name in files:
            if name.endswith(".pyi"):
                dst = os.path.join(root[5:], name)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy(os.path.join(root, name), dst)

# generate api documentation
                # COMMAND ${python} -u ${CMAKE_CURRENT_SOURCE_DIR}/gen_api.py -o ${maixpy_wrapper_src} --doc ${PROJECT_PATH}/docs/api --sdk_path ${SDK_PATH}
maixcdk_path = os.path.abspath(os.environ.get("MAIXCDK_PATH", None))
maixpy_path = os.path.abspath(os.getcwd())
if maixcdk_path.startswith(maixpy_path):
    raise Exception("DO NOT put MaixCDK in MaixPy folder, please put MaixCDK in other place and set MAIXCDK_PATH environment variable by `export MAIXCDK_PATH=xxxxx`")
if not maixcdk_path:
    raise Exception("No environment variable MAIXCDK_PATH, please set first by `export MAIXCDK_PATH=xxxxx`")
ret = os.system(f"python -u components/maix/gen_api.py --doc docs/api --sdk_path {maixcdk_path}")
if ret != 0:
    raise Exception("Generate doc file failed")

# requirement packages
requirements = []

# Read long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Get version info from maix/version.py file
with open("maix/version.py", "r", encoding="utf-8") as f:
    vars = {}
    exec(f.read(), vars)
    __version__ = vars["__version__"]

class BinaryDistribution(Distribution):
    """Distribution which always forces a binary package with platform name"""
    def has_ext_modules(foo):
        return True

pkgs = find_packages()
print("-- found packages: {}".format(pkgs))

setup(
    # all keywords see https://setuptools.pypa.io/en/latest/references/keywords.html

    # Package name
    name='MaixPy',

    # Versions should comply with PEP440: https://peps.python.org/pep-0440/
    version=__version__,

    author='Sipeed',
    author_email='support@sipeed.com',

    description='Sipeed Maix Vision Python SDK',
    long_description=long_description,
    long_description_content_type="text/markdown",

    # The project's main homepage.
    url='https://github.com/Sipeed/MaixPy',

    # All License should comply with https://spdx.org/licenses/
    license='Apache 2.0',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Embedded Systems',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3'
    ],

    # What does your project relate to?
    keywords='Machine vision, AI vision, IOT, AIOT, Edge computing',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=pkgs,

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=requirements,

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        # 'dev': ['check-manifest'],
        # 'test': ['coverage'],
    },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={
        'maix': ['*.so', "dl_lib/*.so*", "*.pyi", "**/*.pyi", "**/**/*.pyi"]
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    data_files=[
	        # ("",["LICENSE","README.md"])
        ],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'maix-resize=maix.maix_resize:main_cli'
        ],
        # 'gui_scripts': [
        # ],
    },

    distclass=BinaryDistribution
)

if board:
    py_tag = "cp{}{}".format(build_py_version[0], build_py_version[1])
    files = os.listdir("dist")
    # 根据文件编辑时间排序，取最新的文件
    files.sort(key=lambda x: os.path.getmtime(os.path.join("dist", x)), reverse=True)
    name = files[0]
    # if name.endswith(".whl"):
    #     os.rename(os.path.join("dist", name), os.path.join("dist",
    #             "MaixPy-{}-{}-{}-{}.whl".format(__version__, py_tag, py_tag, platform_names[board]))
    #     )
    if name.find("linux_riscv64") != -1:
        # pypi not support riscv64 yet, so we have to change to py3-none-any pkg
        # unzip to dist/temp, change dist-info/WHEEL file
        # zip back and rename
        import zipfile
        with zipfile.ZipFile(os.path.join("dist", name), "r") as zip_ref:
            zip_ref.extractall("dist/temp")
        wheel_path = "dist/temp/MaixPy-{}.dist-info/WHEEL".format(__version__)
        if not os.path.exists(wheel_path):
            wheel_path = "dist/temp/maixpy-{}.dist-info/WHEEL".format(__version__)
        with open(wheel_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        with open(wheel_path, "w", encoding="utf-8") as f:
            for line in lines:
                if line.startswith("Tag:"):
                    f.write("Tag: py3-none-any\n")
                else:
                    f.write(line)
        with zipfile.ZipFile(os.path.join("dist", name), "w") as zip_ref:
            for root, dirs, files in os.walk("dist/temp"):
                for file in files:
                    zip_ref.write(os.path.join(root, file), os.path.join(root[9:], file))
        shutil.rmtree("dist/temp")
        os.rename(os.path.join("dist", name), os.path.join("dist",
                "MaixPy-{}-py3-none-any.whl".format(__version__))
        )

