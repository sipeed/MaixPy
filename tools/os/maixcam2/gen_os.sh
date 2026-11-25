#!/bin/bash

set -eo pipefail

usage() {
    cat <<'EOF'
Usage:
  ./gen_os.sh BASE.axp MAIXPY.whl BUILTIN_FILES [SKIP_BUILD_APPS] [maixcam2] [DELETE_FIRST_FILES] [--output img|img-7z|all]
  ./gen_os.sh compress [--build BUILD_ID]
  ./gen_os.sh axp [--build BUILD_ID] [--full]

Build defaults: --output all, SKIP_BUILD_APPS=0.
  img      Generate an uncompressed IMG.
  img-7z   Generate 7z volumes.
  all      Generate 7z volumes and a boot_parts AXP.
The compress and axp commands default to the latest successful IMG build.
Compression defaults to level 9 (override with MAIXCAM2_7Z_LEVEL), in 2 GiB volumes.
Volumes are saved to images/builds/BUILD_ID/7z/; the IMG is removed after verification.
Use --full to also package a full AXP.
EOF
}

die() {
    echo "Error: $*" >&2
    exit 1
}

lock_builds() {
    exec 9<.
    flock -n 9 || die "Another MaixCAM2 build or packaging command is running"
}

compress_img() (
    local build_dir="$1" version="$2"
    local img="$build_dir/$version.img" volumes="$build_dir/7z" stage
    local archive="$version.img.7z"

    if [ -d "$volumes" ]; then
        7z t -bsp0 "$volumes/$archive.001"
        rm -f -- "$img"
        echo "Verified existing volumes (compression skipped): $volumes/$archive.*"
        return
    fi
    [ -s "$img" ] || die "Missing IMG: $img"

    stage=$(mktemp -d "$build_dir/.compress.XXXXXXXX")
    trap 'rm -rf -- "$stage"' EXIT
    (cd "$build_dir" && 7z a -bsp0 -v2g "-mx${MAIXCAM2_7Z_LEVEL:-9}" "$stage/$archive" "$version.img")
    7z t -bsp0 "$stage/$archive.001"
    mv -T -- "$stage" "$volumes"
    rm -- "$img"
    echo "7z volumes: $volumes/$archive.*"
)

# Write the XML first so its local header has a 32-bit offset.
package_axp() (
    local source_dir="$1" output="$2"
    cd "$source_dir"
    local manifests=( *.xml )
    if [ "${#manifests[@]}" -ne 1 ] || [ ! -s "${manifests[0]}" ]; then
        die "Expected one nonempty AXP XML manifest in $source_dir"
    fi
    zip -q "$output" "${manifests[0]}"
    zip -qr "-${MAIXCAM2_ZIP_LEVEL:-1}" "$output" . -x "${manifests[0]}"
    unzip -p "$output" "${manifests[0]}" | cmp "${manifests[0]}" -
    unzip -tq "$output"
)

package_build_axp() (
    local build_dir="$1" version="$2" full="$3" stage name
    local partitions="$build_dir/partitions"
    [ -s "$partitions/ubuntu_rootfs_sparse.ext4" ] || die "Missing saved AXP partitions: $partitions"
    stage=$(mktemp -d "$build_dir/.axp.XXXXXXXX")
    trap 'rm -rf -- "$stage"' EXIT

    mkdir "$stage/boot_parts"
    rsync -a --exclude='/ubuntu_rootfs_sparse.ext4' "$partitions/" "$stage/boot_parts/"
    truncate -s 20M "$stage/boot_parts/ubuntu_rootfs_sparse.ext4"
    name="boot_parts_$version.axp"
    package_axp "$stage/boot_parts" "$stage/$name"
    mv -f -- "$stage/$name" "$build_dir/$name"
    echo "Boot AXP: $build_dir/$name"

    if [ "$full" = 1 ]; then
        name="$version.axp"
        package_axp "$partitions" "$stage/$name"
        mv -f -- "$stage/$name" "$build_dir/$name"
        echo "Full AXP: $build_dir/$name"
    fi
)

if [ "${1:-}" = --help ] || [ "${1:-}" = -h ]; then
    usage
    exit 0
fi
script_dir="$(cd -- "$(dirname -- "$0")" && pwd -P)"
[ "$(pwd -P)" = "$script_dir" ] || die "Run this script from $script_dir"
images_dir="$script_dir/images"
builds_dir="$images_dir/builds"

case "${1:-}" in
    compress|axp)
        action=$1
        shift
        build_id=""
        full=0
        while [ "$#" -gt 0 ]; do
            case "$1" in
                --build)
                    [ "$#" -ge 2 ] && [ -n "$2" ] || die "--build requires a build ID"
                    build_id=$2
                    shift 2
                    ;;
                --full)
                    [ "$action" = axp ] || die "--full is only supported by axp"
                    full=1
                    shift
                    ;;
                *) die "Unknown $action option: $1" ;;
            esac
        done
        lock_builds
        if [ -z "$build_id" ]; then
            latest=$(readlink -- "$images_dir/latest") || die "No saved IMG build. Run gen_os.sh with build inputs first."
            [[ "$latest" == builds/* ]] || die "Invalid latest build pointer"
            build_id=${latest#builds/}
        fi
        [[ "$build_id" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]] || die "Invalid build ID: $build_id"
        build_dir="$builds_dir/$build_id"
        [ -f "$build_dir/version" ] || die "Build not found: $build_id"
        IFS= read -r os_version_str < "$build_dir/version"
        [[ "$os_version_str" =~ ^maixcam2-[0-9-]+-maixpy-v[0-9]+\.[0-9]+\.[0-9]+$ ]] || die "Invalid saved version: $os_version_str"
        echo "Using build $build_id ($os_version_str)"
        if [ "$action" = compress ]; then
            compress_img "$build_dir" "$os_version_str"
        else
            package_build_axp "$build_dir" "$os_version_str" "$full"
        fi
        exit 0
        ;;
esac

output=all
args=()
while [ "$#" -gt 0 ]; do
    case "$1" in
        --output)
            [ "$#" -ge 2 ] || die "--output requires img, img-7z or all"
            output=$2
            shift 2
            ;;
        --*) die "Unknown build option: $1" ;;
        *) args+=("$1"); shift ;;
    esac
done
case "$output" in
    img|img-7z|all) ;;
    *) die "Invalid --output: $output" ;;
esac
if [ "${#args[@]}" -lt 3 ] || [ "${#args[@]}" -gt 6 ]; then
    usage >&2
    exit 1
fi

base_os_path=${args[0]}
whl_path=${args[1]}
builtin_files_dir_path=${args[2]}
skip_build_apps=${args[3]:-0}
board_name=${args[4]:-maixcam2}
delete_first_files=${args[5]:-}
[[ "$skip_build_apps" =~ ^[01]$ ]] || die "SKIP_BUILD_APPS must be 0 or 1"
[ "$board_name" = maixcam2 ] || die "Board must be maixcam2"
if [ -n "$delete_first_files" ]; then
    [ -f "$delete_first_files" ] || die "Delete list not found: $delete_first_files"
fi
[[ -f "$base_os_path" && "$base_os_path" == *.axp ]] || die "Base AXP not found: $base_os_path"
[ -f "$whl_path" ] || die "MaixPy wheel not found: $whl_path"
[ -e "$builtin_files_dir_path" ] || die "Builtin files not found: $builtin_files_dir_path"
[[ "${whl_path##*/}" =~ -([0-9]+\.[0-9]+\.[0-9]+)- ]] || die "Cannot read MaixPy version from wheel: $whl_path"
os_version_str="$board_name-$(date +%F)-maixpy-v${BASH_REMATCH[1]}"
[ -n "$MAIXCDK_PATH" ] || die "MAIXCDK_PATH environment variable is not set"

lock_builds
mkdir -p tmp "$builds_dir"
set -x

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

# Generate an IMG and keep the matching partitions for later packaging.
build_dir=$(mktemp -d "$builds_dir/$os_version_str.XXXXXXXX")
build_id=${build_dir##*/}
build_ready=0
trap 'if [ "$build_ready" = 0 ]; then rm -rf -- "$build_dir"; fi' EXIT
img="$build_dir/$os_version_str.img"

# axp2img creates work directories inside its input directory.
sudo chown -- "$(id -u):$(id -g)" tmp2/axp
python3 "$script_dir/axp-tools/axp_tools/axp2img.py" -i tmp2/axp     -o "$img" --raw-rootfs tmp2/rootfs_new.ext4.raw
test -s "$img"
rm -rf -- tmp2/axp/out tmp2/axp/temp
rm -f -- tmp2/rootfs_new.ext4.raw

mkdir "$build_dir/partitions"
rsync -a --no-owner --no-group --chmod=u+rX tmp2/axp/ "$build_dir/partitions/"
test -s "$build_dir/partitions/ubuntu_rootfs_sparse.ext4"
printf '%s\n' "$os_version_str" > "$build_dir/version"
build_ready=1

ln -s -- "builds/$build_id" "$build_dir/.latest"
mv -Tf -- "$build_dir/.latest" "$images_dir/latest"
echo "Build $build_id ready: $img"

if [ "$output" != img ]; then
    compress_img "$build_dir" "$os_version_str"
fi
if [ "$output" = all ]; then
    package_build_axp "$build_dir" "$os_version_str" 0
fi
