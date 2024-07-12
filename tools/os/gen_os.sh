#!/bin/bash

# 0. 确保环境变量 MAIXCDK_PATH 存在，以及当前目录在 MaixPy/tools 目录下
# 1. 检查参数 文件或者文件夹是否存在，然后拷贝一份 sys_builtin_files 到 tmp 目录，不要影响原目录，检查 base os file 是不是 xz, 如果是解压到临时目录 tmp，不是则拷贝一份到 tmp 目录下 os_version_str.img
# 2. 解压 MaixPy whl 包到临时目录 tmp，并拷贝解压后的所有文件和目录到 sys_builtin_files/usr/lib/python3.11/site-packages 目录
# 3. 打包 MaixPy 写的应用（MaixPy/projects 目录下执行 build_all.sh)，生成 maixapp/apps 目录，将内容全部拷贝到 sys_builtin_files/maixapp/apps 目录
# 4. 打包 MaixCDK 写的应用，进入 $MAIXCDK_PATH/projects， 执行 build_all.sh，生成 maixapp/apps 目录，将内容全部拷贝到 sys_builtin_files/maixapp/apps 目录
# 5. 生成 sys_builtin_files/maixapp/apps/app.info 文件，执行 python gen_app_info.py sys_builtin_files/maixapp/apps
# 6. 写入 sys_builtin_files/boot/ver 版本号文件（使用参数 os_version_str）， 比如 maixcam-2024-05-13-maixpy-v4.1.0
# 7. 拷贝 MaixCDK/components/maixcam_lib/lib/libmaixcam_lib.so 到 sys_builtin_files/usr/lib
# 8. 拷贝 sys_builtin_files 生成新镜像，通过 ./update_img.sh sys_builtin_files tmp/os_version_str.img
# 9. xz 压缩镜像

set -e
set -x

function usage() {
    echo "Usage:"
    echo "      ./gen_os.sh base_os_filepath maixpy_whl_filepath builtin_files_dir_path os_version_str"
    echo ""
}

if [ "$#" -ne 4 ]; then
    usage
    exit 1
fi

base_os_path=$1
whl_path=$2
builtin_files_dir_path=$3
os_version_str=$4

# 0. 确保环境变量 MAIXCDK_PATH 存在，以及当前目录在 MaixPy/tools 目录下
if [ -z "$MAIXCDK_PATH" ]; then
    echo "Error: MAIXCDK_PATH environment variable is not set."
    exit 1
fi

if [ "$(basename $PWD)" != "os" ] || [ "$(basename $(dirname $PWD))" != "tools" ]; then
    echo "Error: Script must be run from MaixPy/tools/os directory."
    exit 1
fi

# 删除之前的缓存文件
rm -rf tmp/maixpy_whl
rm -rf tmp/sys_builtin_files
rm -rf tmp/*.img
rm -rf tmp/$os_version_str.img.xz
sync

# 1. 检查参数 文件或者文件夹是否存在，然后拷贝一份 builtin_files_dir_path 到 tmp，不要影响原目录，检查 base os file 是不是 xz, 如果是解压到临时目录 tmp，并改名为 os_version_str.img，不是则拷贝一份到 tmp 目录下 os_version_str.img
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
mkdir -p tmp/maixpy_whl
unzip "$whl_path" -d tmp/maixpy_whl
mkdir -p tmp/sys_builtin_files/usr/lib/python3.11/site-packages
cp -r tmp/maixpy_whl/* tmp/sys_builtin_files/usr/lib/python3.11/site-packages

# 3. 打包 MaixPy 写的应用（MaixPy/projects 目录下执行 build_all.sh)，生成 apps 目录，将内容全部拷贝到 tmp/sys_builtin_files/apps 目录
cd ../../projects
chmod +x ./build_all.sh
./build_all.sh
cd -
mkdir -p tmp/sys_builtin_files/maixapp/apps
cp -r ../../projects/apps/* tmp/sys_builtin_files/maixapp/apps

# 4. 打包 MaixCDK 写的应用，进入 $MAIXCDK_PATH/projects， 执行 build_all.sh，生成 apps 目录，将内容全部拷贝到 tmp/sys_builtin_files/apps 目录
cd "$MAIXCDK_PATH/projects"
chmod +x ./build_all.sh
./build_all.sh
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
cp "$MAIXCDK_PATH/components/maixcam_lib/lib/libmaixcam_lib.so" tmp/sys_builtin_files/usr/lib

# 8. 拷贝 tmp/sys_builtin_files 生成新镜像，通过 ./update_img.sh tmp/sys_builtin_files tmp/os_version_str.img
./update_img.sh tmp/sys_builtin_files "tmp/$os_version_str.img"

# 9. xz 压缩镜像
xz -zv "tmp/$os_version_str.img"

echo "Complete: os file: tmp/$os_version_str.img.xz"


