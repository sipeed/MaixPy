#!/bin/bash

# 0. 确保环境变量 MAIXCDK_PATH 存在，以及当前目录在 MaixPy/tools 目录下
# 1. 检查参数 文件或者文件夹是否存在，然后拷贝一份 sys_builtin_files 到 tmp 目录，不要影响原目录，检查 base os file 是不是 xz, 如果是解压到临时目录 tmp，不是则拷贝一份到 tmp 目录下 os_version_str.img
# 2. 解压 MaixPy whl 包到临时目录 tmp，并拷贝解压后的所有文件和目录到 sys_builtin_files/usr/lib/python3.11/site-packages 目录
# 3. 打包 MaixPy 写的应用（MaixPy/projects 目录下执行 build_all.sh)，生成 maixapp/apps 目录，将内容全部拷贝到 sys_builtin_files/maixapp/apps 目录
# 4. 打包 MaixCDK 写的应用，进入 $MAIXCDK_PATH/projects， 执行 build_all.sh，生成 maixapp/apps 目录，将内容全部拷贝到 sys_builtin_files/maixapp/apps 目录
# 5. 生成 sys_builtin_files/maixapp/apps/app.info 文件，执行 python gen_app_info.py sys_builtin_files/maixapp/apps
# 6. 拷贝 MaixCDK/components/maixcam_lib/lib/libmaixcam_lib.so 到 sys_builtin_files/usr/lib
# 7. 拷贝 sys_builtin_files 生成新镜像，通过 ./update_img.sh sys_builtin_files tmp/os_version_str.img
# 8. xz 压缩镜像

set -e
set -x

function usage() {
    echo "Usage:"
    echo "      ./gen_os.sh <base_os_filepath> <maixpy_whl_filepath> <builtin_files_dir_path> [skip_build_apps] [board_name]"
    echo "skip_build_apps can be 0 or 1"
    echo "board_name can be maixcam or maixcam-pro"
    echo ""
}

param_count=$#
if [ "$param_count" -ne 3 ] && [ "$param_count" -ne 4 ] && [ "$param_count" -ne 5 ]; then
    usage
    exit 1
fi

base_os_path=$1
whl_path=$2
builtin_files_dir_path=$3
skip_build_apps=0
board_name=maixcam

# 如果提供了第五个参数且不为空，则将 skip_build_apps 设置为 1
if [ -n "$4" ]; then
    if [ "x$4" == "x1" ]; then
        skip_build_apps=1
    elif [ "x$4" != "x0" ]; then
        echo "skip_build_apps arg should be 0 or 1"
        exit 1
    fi
fi

if [ -n "$5" ]; then
    if [ "x$5" == "xmaixcam" ]; then
        board_name=maixcam
    elif [ "x$5" == "xmaixcam-pro" ]; then
        board_name=maixcam-pro
    else
        echo "board_name arg should be maixcam or maixcam-pro"
        exit 1
    fi
fi

# 设置输出的镜像名字 maixcam-2024-10-31-maixpy-v4.7.8
date_now=$(date +"%Y-%m-%d")
maixpy_version=$(echo "$whl_path" | grep -oP '(?<=MaixPy-)[^-]+')
os_version_str=${board_name}-${date_now}-maixpy-v${maixpy_version}


# 0. 确保环境变量 MAIXCDK_PATH 存在，以及当前目录在 MaixPy/tools 目录下
if [ -z "$MAIXCDK_PATH" ]; then
    echo "Error: MAIXCDK_PATH environment variable is not set."
    exit 1
fi

if [ "$(basename $PWD)" != "maixcam" ] || [ "$(basename $(dirname $PWD))" != "os" ]; then
    echo "Error: Script must be run from MaixPy/tools/os/maixcam directory."
    exit 1
fi

# 删除之前的缓存文件
rm -rf tmp/maixpy_whl
rm -rf tmp/sys_builtin_files
rm -rf tmp/*.img
rm -rf tmp/$os_version_str.img.xz
sync

# 1. 检查参数 文件或者文件夹是否存在，然后拷贝一份 builtin_files_dir_path 到 tmp，不要影响原目录，检查 base os file 是不是 xz, 如果是解压到临时目录 tmp，并改名为 os_version_str.img，不是则拷贝一份到 tmp 目录下 os_version_str.img
echo "copy builtin files"
if [ ! -e "$base_os_path" ]; then
    echo "Error: Base OS file does not exist."
    exit 1
fi

mkdir -p tmp
cp -r "$builtin_files_dir_path" tmp/sys_builtin_files

if file "$base_os_path" | grep -q 'XZ compressed data'; then
    xz -dkc "$base_os_path" > "tmp/$os_version_str.img"
else
    cp "$base_os_path" "tmp/$os_version_str.img"
fi

# 2. 解压 MaixPy whl 包到临时目录 tmp，并拷贝解压后的所有文件和目录到 tmp/sys_builtin_files/usr/lib/python3.11/site-packages 目录
echo "copy MaixPy files"
mkdir -p tmp/maixpy_whl
unzip "$whl_path" -d tmp/maixpy_whl
mkdir -p tmp/sys_builtin_files/usr/lib/python3.11/site-packages
cp -r tmp/maixpy_whl/* tmp/sys_builtin_files/usr/lib/python3.11/site-packages

# 3. 打包 MaixPy 写的应用（MaixPy/projects 目录下执行 build_all.sh)，生成 apps 目录，将内容全部拷贝到 tmp/sys_builtin_files/apps 目录
echo "pack and copy MaixPy projects"
cd ../../../projects
if [ $skip_build_apps == 0 ]; then
    chmod +x ./build_all.sh
    ./build_all.sh
fi
cd -
mkdir -p tmp/sys_builtin_files/maixapp/apps
cp -r ../../../projects/apps/* tmp/sys_builtin_files/maixapp/apps

# 4. 打包 MaixCDK 写的应用，进入 $MAIXCDK_PATH/projects， 执行 build_all.sh，生成 apps 目录，将内容全部拷贝到 tmp/sys_builtin_files/apps 目录
echo "pack and copy MaixCDK projects"
cd "$MAIXCDK_PATH/projects"
if [ $skip_build_apps == 0 ]; then
    chmod +x ./build_all.sh
    ./build_all.sh
fi
cd -
cp -r $MAIXCDK_PATH/projects/apps/* tmp/sys_builtin_files/maixapp/apps

# 5. 生成 tmp/sys_builtin_files/maixapp/apps/app.info 文件，执行 python gen_app_info.py tmp/sys_builtin_files/maixapp/apps
cp -f gen_app_info.py tmp/sys_builtin_files/maixapp/apps
python gen_app_info.py tmp/sys_builtin_files/maixapp/apps

# 6. 写入 tmp/sys_builtin_files/boot/ver 版本号文件（使用参数 os_version_str）， 比如 maixcam-2024-05-13-maixpy-v4.1.0
mkdir -p tmp/sys_builtin_files/boot
echo "$os_version_str" > tmp/sys_builtin_files/boot/ver

# 7. 拷贝 MaixCDK/components/maixcam_lib/lib/libmaixcam_lib.so 到 tmp/sys_builtin_files/usr/lib
mkdir -p tmp/sys_builtin_files/usr/lib
cp "$MAIXCDK_PATH/components/maixcam_lib/lib_maixcam/libmaixcam_lib.so" tmp/sys_builtin_files/usr/lib

# 8. 不同板型拷贝
if [ $board_name == "maixcam-pro" ]; then
    cp -f "tmp/sys_builtin_files/boot/maixcam_pro_logo.jpeg" "tmp/sys_builtin_files/boot/logo.jpeg"
    cp "tmp/sys_builtin_files/boot/boards/board.maixcam_pro" "tmp/sys_builtin_files/boot/board"
else
    cp "tmp/sys_builtin_files/boot/boards/board.maixcam" "tmp/sys_builtin_files/boot/board"
fi
# 8.2 因为 boot分区不能拷贝文件夹，将 boards 文件夹拷贝到 /maixapp/boards，等第一次开机脚本复制到 boot 分区
cp -r "tmp/sys_builtin_files/boot/boards" "tmp/sys_builtin_files/maixapp/"

# 9. 拷贝 tmp/sys_builtin_files 生成新镜像，通过 ./update_img.sh tmp/sys_builtin_files tmp/os_version_str.img
./update_img.sh tmp/sys_builtin_files "tmp/$os_version_str.img"

# 9. xz 压缩镜像
xz -zv -T 0 "tmp/$os_version_str.img"

echo "Complete: os file: tmp/$os_version_str.img.xz"


