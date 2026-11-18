#!/bin/bash

# 0. 确保环境变量 MAIXCDK_PATH 存在，以及当前目录在 MaixPy/tools 目录下
# 1. 检查参数 文件或者文件夹是否存在，然后拷贝一份 sys_builtin_files 到 tmp 目录，不要影响原目录，检查 base os file 是不是 xz, 如果是解压到临时目录 tmp，不是则拷贝一份到 tmp 目录下 os_version_str.img
# 2. 解压 MaixPy whl 包到临时目录 tmp，并拷贝解压后的所有文件和目录到 sys_builtin_files/usr/local/lib/python3.13/site-packages 目录
# 3. 打包 MaixPy 写的应用（MaixPy/projects 目录下执行 build_all.sh)，生成 maixapp/apps 目录，将内容全部拷贝到 sys_builtin_files/maixapp/apps 目录
# 4. 打包 MaixCDK 写的应用，进入 $MAIXCDK_PATH/projects， 执行 build_all.sh，生成 maixapp/apps 目录，将内容全部拷贝到 sys_builtin_files/maixapp/apps 目录
# 5. 生成 sys_builtin_files/maixapp/apps/app.info 文件，执行 python gen_app_info.py sys_builtin_files/maixapp/apps
# 6. 拷贝 MaixCDK/components/maixcam_lib/lib/libmaixcam_lib.so 到 sys_builtin_files/usr/lib
# 7. 拷贝 sys_builtin_files 生成新镜像，通过 ./update_img.sh sys_builtin_files tmp/os_version_str.img
# 8. xz 压缩镜像

set -e

function usage() {
    echo "Usage:"
    echo "      ./gen_os.sh <base_os_filepath> <maixpy_whl_filepath> <builtin_files_dir_path> <skip_build_apps> <board_name> [generate_axp_full] [delete_first_files]"
    echo "skip_build_apps can be 0 or 1"
    echo "board_name can be maixcam or maixcam-pro"
    echo "generate_axp_full if 0 will only generate boot_parts axp, default 0"
    echo "delete_first_files before copy new builtin files, delete some files, one line one item, format same with command rm,"
    echo "you can also create a delete_first.txt in builtin_files_dir and leave this arg empty"
    echo ""
    echo "Example:"
    echo "      ./gen_os.sh AX630C_emmc_arm64_k419_sipeed_maixcam2_ubuntu_rootfs_V3.0.0_20250319114413_20251009154249_glibc.axp \
                            build/maixpy-4.12.1-cp313-cp313-manylinux2014_aarch64.whl \
                            maixcam2_builtin_files \
                            1 \
                            maixcam2 \
                            1"
}

function check_axp2img_command() {
    if ! command -v axp2img >/dev/null 2>&1; then
        echo "axp2img command not found, please run \"pip install axp-tools\" first"
        exit 1
    fi
}

param_count=$#
case "$param_count" in
    3|4|5|6|7)
        ;;
    *)
        usage
        exit 1
        ;;
esac

base_os_path=$1
whl_path=$2
builtin_files_dir_path=$3
skip_build_apps=0
board_name=maixcam
generate_axp_full=0
package_method="7z"

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
    if [ "x$5" == "xmaixcam2" ]; then
        board_name=maixcam2
    else
        echo "board_name arg should be maixcam2"
        exit 1
    fi
fi

# check_axp2img_command

if [ -n "$6" ]; then
    if [ "x$6" == "x1" ]; then
        generate_axp_full=1
    elif [ "x$6" != "x0" ]; then
        echo "generate_axp_full arg should be 0 or 1"
        exit 1
    fi
fi

delete_first_files=""
if [ -n "$7" ]; then
    delete_first_files=$7
    if [[ ! -e "$delete_first_files" ]]; then
        echo "Error: delete_first_files $delete_first_files file does not exist"
        exit 1
    fi
fi

# 检查镜像文件
if [[ ! -e "$base_os_path" || "${base_os_path##*.}" != "axp" ]]; then
    echo "Error: Base OS file does not exist or is not an .axp file."
    exit 1
fi

if [ ! -f "$whl_path" ]; then
    echo "MaixPy wheel $whl_path not found!!!"
    usage
    exit 1
fi

if [ ! -e "$builtin_files_dir_path" ]; then
    echo "builtin_files_dir_path $builtin_files_dir_path not found!!!"
    usage
    exit 1
fi

set -x

# 设置输出的镜像名字 maixcam2-2025-04-16-maixpy-v4.11.0
date_now=$(date +"%Y-%m-%d")
maixpy_version=$(echo "$whl_path" | sed -E 's/.*-([0-9]+\.[0-9]+\.[0-9]+)-.*/\1/')
os_version_str=${board_name}-${date_now}-maixpy-v${maixpy_version}


# 0. 确保环境变量 MAIXCDK_PATH 存在，以及当前目录在 MaixPy/tools 目录下
if [ -z "$MAIXCDK_PATH" ]; then
    echo "Error: MAIXCDK_PATH environment variable is not set."
    exit 1
fi

if [ "$(basename $PWD)" != "maixcam2" ] || [ "$(basename $(dirname $PWD))" != "os" ]; then
    echo "Error: Script must be run from MaixPy/tools/os/maixcam2 directory."
    exit 1
fi

# A build owns the shared staging directories until its outputs are published.
mkdir -p tmp
exec 9<.
flock -n 9 || { echo "Another MaixCAM2 build is using tmp/tmp2" >&2; exit 1; }

# 删除之前的缓存文件
rm -rf tmp/maixpy_whl
rm -rf tmp/sys_builtin_files
rm -rf tmp/*.img
rm -rf tmp/$os_version_str.img.xz
rm -rf tmp/delete_files.txt

# get sudo permission for update_img.sh later
echo -e "\n\n======================================\nFor MaixCDK/MaixPy maintainer:\n    DON'T forget to update APPs like launcher, settings, app_store in builtin_files !!\n\nNeed sudo permission for update_img.sh later, grant permission now\n======================================\n"
sudo echo ""


# 1. 检查参数 文件或者文件夹是否存在，然后拷贝一份 builtin_files_dir_path 到 tmp，不要影响原目录，检查 base os file 是不是 xz, 如果是解压到临时目录 tmp，并改名为 os_version_str.img，不是则拷贝一份到 tmp 目录下 os_version_str.img
echo "copy builtin files"

mkdir -p tmp
# if builtin_files_dir_path is a xz or tar.xz file, unzip it to tmp/builtin_files_dir_path
if [[ "$builtin_files_dir_path" == *.tar.xz ]]; then
    archive_dir=tmp/builtin_archive
    rm -rf -- "$archive_dir"
    mkdir "$archive_dir"
    tar -Jxf "$builtin_files_dir_path" -C "$archive_dir"
    archive_name=$(basename -- "$builtin_files_dir_path" .tar.xz)
    for layout in "$archive_dir/$archive_name" "$archive_dir/sys_builtin_files" "$archive_dir"; do
        if [ -d "$layout/boot" ]; then
            mv -- "$layout" tmp/sys_builtin_files
            break
        fi
    done
elif [ -d "$builtin_files_dir_path" ]; then
    mkdir tmp/sys_builtin_files
    cp -a "$builtin_files_dir_path/." tmp/sys_builtin_files/
    # Resolve shared build-host data without dereferencing links inside it.
    for shared_path in usr root/models; do
        source_path="$builtin_files_dir_path/$shared_path"
        if [ -L "$source_path" ]; then
            if [ ! -d "$source_path" ]; then
                echo "Shared directory is missing: $source_path" >&2
                exit 1
            fi
            rm -- "tmp/sys_builtin_files/$shared_path"
            cp -a -- "$source_path/" "tmp/sys_builtin_files/$shared_path"
        fi
    done
    # Copy per-model links to the shared build-host directory into the image.
    for model_link in "$builtin_files_dir_path"/root/models/*; do
        [ -L "$model_link" ] || continue
        model_name=${model_link##*/}
        [ "$(readlink -- "$model_link")" = "../../../models/$model_name" ] || continue
        model_source=$(realpath -e -- "$model_link") || exit 1
        staged_model="tmp/sys_builtin_files/root/models/$model_name"
        rm -- "$staged_model" || exit 1
        cp -a -- "$model_source" "$staged_model" || exit 1
    done
else
    echo "builtin_files_dir_path must be a directory or .tar.xz archive"
    exit 1
fi

if [ ! -d "tmp/sys_builtin_files" ]; then
    echo "sys_builtin_files file must contain sys_builtin_files directory"
    exit 1
fi

# 2. 解压 MaixPy whl 包到临时目录 tmp，并拷贝解压后的所有文件和目录到 tmp/sys_builtin_files/usr/lib/python3.11/site-packages 目录
echo "copy MaixPy files"
mkdir -p tmp/maixpy_whl
unzip "$whl_path" -d tmp/maixpy_whl
mkdir -p tmp/sys_builtin_files/usr/local/lib/python3.13/site-packages
cp -r tmp/maixpy_whl/* tmp/sys_builtin_files/usr/local/lib/python3.13/site-packages

# 3. 打包 MaixPy 写的应用（MaixPy/projects 目录下执行 build_all.sh)，生成 apps 目录，将内容全部拷贝到 tmp/sys_builtin_files/apps 目录
echo "pack and copy MaixPy projects"
cd ../../../projects
if [ $skip_build_apps == 0 ]; then
    chmod +x ./build_all.sh
    ./build_all.sh maixcam2
fi
cd -
mkdir -p tmp/sys_builtin_files/maixapp/apps
cp -r ../../../projects/maixcam2_apps/* tmp/sys_builtin_files/maixapp/apps

# 4. 打包 MaixCDK 写的应用，进入 $MAIXCDK_PATH/projects， 执行 build_all.sh，生成 apps 目录，将内容全部拷贝到 tmp/sys_builtin_files/apps 目录
echo "pack and copy MaixCDK projects"
cd "$MAIXCDK_PATH/projects"
if [ $skip_build_apps == 0 ]; then
    chmod +x ./build_all.sh
    ./build_all.sh maixcam2
fi
cd -
if [ -d $MAIXCDK_PATH/projects/maixcam2_apps/ ]; then
    cp -r $MAIXCDK_PATH/projects/maixcam2_apps/* tmp/sys_builtin_files/maixapp/apps
fi

# 5. 生成 tmp/sys_builtin_files/maixapp/apps/app.info 文件，执行 python gen_app_info.py tmp/sys_builtin_files/maixapp/apps
app_dir=tmp/sys_builtin_files/maixapp/apps
if [ ! -f "$app_dir/gen_app_info.py" ]; then
    cp ../../gen_app_info.py "$app_dir/gen_app_info.py"
fi
python "$app_dir/gen_app_info.py" "$app_dir"

# 6. 写入 tmp/sys_builtin_files/boot/ver 版本号文件（使用参数 os_version_str）， 比如 maixcam-2024-05-13-maixpy-v4.1.0
mkdir -p tmp/sys_builtin_files/boot
echo "$os_version_str" > tmp/sys_builtin_files/boot/ver

# 7. 拷贝 MaixCDK/components/maixcam_lib/lib/libmaixcam_lib.so 到 tmp/sys_builtin_files/usr/lib
mkdir -p tmp/sys_builtin_files/usr/lib
cp "$MAIXCDK_PATH/components/maixcam_lib/lib_maixcam2/libmaixcam_lib.so" tmp/sys_builtin_files/usr/lib

# 8. 不同板型拷贝
cp "tmp/sys_builtin_files/boot/boards/board.maixcam2" "tmp/sys_builtin_files/boot/board"

# 9. 生成需要删除的文件列表
if [ -n "$delete_first_files" ]; then
    cp -- "$delete_first_files" tmp/delete_files.txt
elif [ -e "tmp/sys_builtin_files/delete_first.txt" ]; then
    mv "tmp/sys_builtin_files/delete_first.txt" tmp/delete_files.txt
else
    echo "" > tmp/delete_files.txt
fi
delete_first_files=tmp/delete_files.txt

# 9. 拷贝 tmp/sys_builtin_files 生成新镜像，通过 ./update_img.sh tmp/sys_builtin_files tmp/os_version_str.img
echo "Now update system image, need sudo permition to mount rootfs:"
sudo ./update_img.sh "$base_os_path" tmp/sys_builtin_files "$delete_first_files" "" --keep-raw-rootfs
echo "Complete: os dir: tmp2/axp"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
mkdir -p images
echo "Now convert to binary img file: images/${os_version_str}.img.${package_method}"
sudo chmod 777 tmp2/axp
# axp2img
python3 "${SCRIPT_DIR}/axp-tools/axp_tools/axp2img.py" -i tmp2/axp \
    -o "images/${os_version_str}.img.${package_method}" --raw-rootfs tmp2/rootfs_new.ext4.raw \
    --7z-level "${MAIXCAM2_7Z_LEVEL:-3}"
rm -rf tmp2/axp/out tmp2/axp/temp
rm -f -- tmp2/rootfs_new.ext4.raw
echo "Complete convert to binary img file: images/${os_version_str}.img.${package_method}"

# Place the partition manifest before large members so it has a 32-bit offset,
# and verify that it can be read from the completed archive.
package_axp() (
    local source_dir="$1" output="$2"
    cd "$source_dir"
    local manifests=( *.xml )
    if [ "${#manifests[@]}" -ne 1 ] || [ ! -s "${manifests[0]}" ]; then
        echo "Expected one nonempty AXP XML manifest in $source_dir" >&2
        return 1
    fi
    rm -f -- "$output"
    zip -q "$output" "${manifests[0]}"
    zip -qr "-${MAIXCAM2_ZIP_LEVEL:-1}" "$output" . -x "${manifests[0]}"
    unzip -p "$output" "${manifests[0]}" | cmp "${manifests[0]}" -
)

echo "Now zip boot_parts axp file"
mkdir -p tmp2/axp2
rsync -a --exclude='ubuntu_rootfs_sparse.ext4' tmp2/axp/ tmp2/axp2/
dd if=/dev/zero of=tmp2/axp2/ubuntu_rootfs_sparse.ext4 bs=1M count=20
out_path="$(realpath tmp)/boot_parts_${os_version_str}.axp"
package_axp tmp2/axp2 "$out_path"
mv -- "$out_path" "images/boot_parts_${os_version_str}.axp"

if [ "$generate_axp_full" = 1 ]; then
    echo "Now zip axp whole system file"
    out_path="$(realpath tmp)/${os_version_str}.axp"
    package_axp tmp2/axp "$out_path"
    mv -- "$out_path" "images/${os_version_str}.axp"
else
    echo "generate_axp_full is 0, Skip generate full axp"
fi
