#!/bin/bash

###
#    update_image.sh <xxxx.axp> <builtin_files.tar.xz/builtin_files_dir> <delete_first_files.txt> <out_path>
###

set -e

axp_file=$1
builtin_files=$2
delete_first_files=$3
out_path=$4

rootfs_name=ubuntu_rootfs_sparse.ext4
bootfs_name=bootfs.fat32

# check root permition
if [ "$(id -u)" -ne 0 ]; then
  echo "please run this script with root permition(use sudo or run with user root)"
  exit 1
fi


# help funtion
function help() {
    echo "Usage: $0 <axp_file> <builtin_files> <delete_first_files> [rootfs_size]"
    echo "    axp_file:           the axp file to be updated"
    echo "    builtin_files:      the directory or tar.xz file containing the files to be copied"
    echo "    delete_first_files: the file containing the list of files to be deleted first"
    echo "    out_path:           output file name(path)"
    echo "    rootfs_size:        the size of the rootfs image, unit M, (default original image size)"
}

if [ -z "$axp_file" ]; then
    help
    exit 1
fi
if [ -z "$builtin_files" ]; then
    help
    exit 1
fi
if [ -z "$delete_first_files" ]; then
    help
    exit 1
fi
if [ ! -f "$axp_file" ]; then
    echo "File $axp_file not found!"
    exit 1
fi
# builtin_files can be a directory or a tar.xz file
if [ ! -d "$builtin_files" ] && [[ "$builtin_files" != *.tar.xz ]]; then
    echo "File $builtin_files not found or not xz/tar.xz file!"
    exit 1
fi
if [ ! -f "$delete_first_files" ]; then
    echo "File $delete_first_files not found!"
    exit 1
fi

for mount_dir in tmp2/rootfs tmp2/bootfs; do
    if mountpoint -q "$mount_dir"; then
        echo "Existing mount at $mount_dir; unmount it before retrying" >&2
        exit 1
    fi
done

cleanup_mounts() {
    local status=$?
    for mount_dir in tmp2/bootfs tmp2/rootfs; do
        if mountpoint -q "$mount_dir"; then
            umount "$mount_dir" || status=1
        fi
    done
    exit "$status"
}
trap cleanup_mounts EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

rm -rf tmp2/*
mkdir -p tmp2
chmod 777 tmp2

if [[ "$builtin_files" == *.tar.xz && ! -d "$builtin_files" ]]; then
    archive_dir=tmp2/builtin_archive
    mkdir "$archive_dir"
    tar -Jxf "$builtin_files" -C "$archive_dir"
    archive_name=$(basename -- "$builtin_files" .tar.xz)
    if [ -d "$archive_dir/$archive_name" ]; then
        builtin_files="$archive_dir/$archive_name"
    elif [ -d "$archive_dir/sys_builtin_files" ]; then
        builtin_files="$archive_dir/sys_builtin_files"
    else
        builtin_files="$archive_dir"
    fi
fi

# unzip axp_file
echo "Unzipping $axp_file"
mkdir -p tmp2/axp
unzip -q "$axp_file" -d tmp2/axp
if [ $? -ne 0 ]; then
    echo "Failed to unzip $axp_file"
    exit 1
fi
echo "Unzipping $axp_file done"

echo "Converting $axp_file to raw image"
./make_ext4fs/simg2img tmp2/axp/${rootfs_name} tmp2/rootfs.ext4.raw
if [ $? -ne 0 ]; then
    echo "Failed to convert $rootfs_name to raw image"
    exit 1
fi
echo "Converting $axp_file to raw image done"

echo "Mounting raw image to tmp2/rootfs"
mkdir -p tmp2/rootfs
if [ $? -ne 0 ]; then
    echo "Failed to create tmp2/rootfs directory"
    exit 1
fi
mount -t ext4 tmp2/rootfs.ext4.raw tmp2/rootfs
echo "Mounting raw image to tmp2/rootfs done"

echo "Deleting files in $delete_first_files"
root_mount=$(realpath tmp2/rootfs)
while IFS= read -r line || [ -n "$line" ]; do
    line=${line%$'\r'}
    line=${line#/}
    while [[ "$line" == */ ]]; do line=${line%/}; done
    case "$line" in
        ""|\#*) continue ;;
    esac
    target="$root_mount/$line"
    parent=$(realpath -m -- "$(dirname -- "$target")")
    case "/$line/" in
        */../*|*/./*) echo "Invalid rootfs deletion path: $line" >&2; exit 1 ;;
    esac
    case "$parent/" in
        "$root_mount/"*) ;;
        *) echo "Rootfs deletion path escapes image: $line" >&2; exit 1 ;;
    esac
    echo "Deleting rootfs entry: $line"
    rm -rf -- "${target%/}"
done < "$delete_first_files"

# copy builtin_files rootfs
echo "Copying files from directory $builtin_files"
target_rootfs_path=tmp2/rootfs
# copy to new dir
rm -rf tmp2/rootfs_new
mkdir tmp2/rootfs_new
cp -rP tmp2/rootfs/* tmp2/rootfs_new/
target_rootfs_path=tmp2/rootfs_new
# copy rootfs files
find "$builtin_files" -mindepth 1 -maxdepth 1 -type d ! -name "boot" | while read -r dir; do
    cp -rP "$dir" "$target_rootfs_path"
done

# Apply the optional builtin WiFi patch to the staged rootfs.
wifi_patch="$builtin_files/opt/scripts/wifi_patch.py"
if [ -f "$wifi_patch" ]; then
    wifi_script="$target_rootfs_path/opt/scripts/wifi.sh"
    md5sum "$wifi_script"
    python3 "$wifi_patch" --script "$wifi_script"
    md5sum "$wifi_script"
fi

# copy boot files
if [[ -e ${builtin_files}/boot ]]; then
    echo "Copying boot files from ${builtin_files}/boot..."
    mkdir -p tmp2/bootfs
    mount -o loop,rw tmp2/axp/$bootfs_name tmp2/bootfs
    cp -rfP ${builtin_files}/boot/* tmp2/bootfs/
    # Ask initramfs to grow the regenerated ext4 filesystem on first eMMC boot.
    touch tmp2/bootfs/check_resize2fs
    umount tmp2/bootfs
    echo "Copying boot files done"
fi

# Verify space available to applications before converting to Android sparse format.
minimum_free_mib=64
mib=$((1024 * 1024))
minimum_free_bytes=$((minimum_free_mib * mib))
raw_rootfs=tmp2/rootfs_new.ext4.raw
sparse_rootfs="tmp2/axp/$rootfs_name"

# Size the merged tree once. Use logical sizes to allow for files that
# were sparse or shared on the build host.
du_result=$(du -s --apparent-size --count-links --block-size=1M "$target_rootfs_path")
rootfs_data_mib=${du_result%%[[:space:]]*}
# Allow for ext4 metadata, journal and block rounding in addition to free space.
metadata_mib=$(((rootfs_data_mib + 19) / 20 + 32))
rootfs_image_size=$((rootfs_data_mib + metadata_mib + minimum_free_mib))
echo "Rootfs data: $rootfs_data_mib MiB, metadata allowance: $metadata_mib MiB, initial size: $rootfs_image_size MiB"

for attempt in 1 2 3; do
    rm -f -- "$raw_rootfs"
    # Keep the base image's ext4 feature set for the target kernel and tools.
    mke2fs -q -t ext4 -F -b 4096 -I 256 -m 0 \
        -O none,has_journal,ext_attr,resize_inode,filetype,extent,sparse_super,large_file,uninit_bg \
        -d "$target_rootfs_path" "$raw_rootfs" "${rootfs_image_size}M"
    superblock=$(LC_ALL=C dumpe2fs -h "$raw_rootfs")
    available_bytes=$(awk -F: '
        $1 == "Free blocks" { free = $2 + 0 }
        $1 == "Reserved block count" { reserved = $2 + 0 }
        $1 == "Block size" { size = $2 + 0 }
        END {
            if (free == "" || reserved == "" || size <= 0) exit 1
            printf "%.0f\n", (free > reserved ? free - reserved : 0) * size
        }
    ' <<< "$superblock")
    echo "Rootfs available space: $available_bytes bytes (minimum: $minimum_free_bytes)"
    if [ "$available_bytes" -ge "$minimum_free_bytes" ]; then
        break
    fi

    # Round up the deficit and leave room for metadata added as ext4 grows.
    growth_mib=$(((minimum_free_bytes - available_bytes + mib - 1) / mib + 16))
    rootfs_image_size=$((rootfs_image_size + growth_mib))
    echo "Increasing rootfs target to $rootfs_image_size MiB"
done

if [ "$available_bytes" -lt "$minimum_free_bytes" ]; then
    echo "Rootfs has less than $minimum_free_mib MiB available after formatting" >&2
    exit 1
fi

rm -f -- "$sparse_rootfs"
./make_ext4fs/img2simg "$raw_rootfs" "$sparse_rootfs"
if [ "${5:-}" != --keep-raw-rootfs ]; then
    rm -f -- "$raw_rootfs"
fi
echo "Making sparse rootfs done"

# unmount rootfs
echo "Umounting raw rootfs"
umount tmp2/rootfs
if [ $? -ne 0 ]; then
    echo "Failed to unmount tmp2/rootfs"
    exit 2
fi
rm -f tmp2/rootfs.ext4.raw
rm -rf tmp2/rootfs
echo "umount raw rootfs done"

# zip axp
if [[ x$out_path != x ]]; then
    parent_dir=$(dirname "$out_path")
    name=$(basename $out_path)
    out_path=$(realpath $parent_dir)/$name
    echo "Zipping axp file to $out_path"
    mkdir -p $parent_dir
    cd tmp2/axp
    zip -r $out_path .
    cd -
    echo "Zip axp file done"
else
    echo "not zip axp, files in tmp2/axp"
fi

echo "All OK"

