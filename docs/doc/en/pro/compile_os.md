---
title: Building the System for MaixCAM
---

## Customizing and Compiling the System

You can download the latest system suitable for MaixCAM from [https://github.com/sipeed/MaixPy/releases](https://github.com/sipeed/MaixPy/releases).

For the latest base system, download it from [https://github.com/sipeed/LicheeRV-Nano-Build/releases](https://github.com/sipeed/LicheeRV-Nano-Build/releases). Please note that this system cannot be directly flashed to MaixCAM as it may damage the screen.

For system source code and compilation instructions, refer to [https://github.com/sipeed/LicheeRV-Nano-Build](https://github.com/sipeed/LicheeRV-Nano-Build). It is recommended to use the Docker compilation method mentioned in the README to avoid compilation issues (note that the compiled system cannot be directly flashed to MaixCAM as it may damage the screen).

## Copying Files for MaixCAM

After compilation, you will get an img file. For MaixCAM, additional files need to be added to this img file. Download the [compressed package](https://github.com/sipeed/MaixPy/releases/download/v4.3.2/sys_builtin_files_2024.6.19.tar.xz), extract it, and save the script from the appendix as `update_img.sh`. Copy the `img` file, then execute `./update_img.sh path_to_sys_builtin_files path_to_copied_img`. This `img` can now be used for flashing to MaixCAM.

However, note that the compressed package is of version `v4.3.2` and not the latest version. Adjust its contents according to your needs. Additionally, MaixPy is in the `usr/lib` directory, which can also be manually updated.

## Appendix `update_img.sh`:

```shell
#!/bin/sh

set -e

source_dir=$1
img_file=$2
mount_root=img_root

img_file=$(readlink -f "$img_file")
THISDIR=$(dirname $(realpath $0))

if [ -z $img_file ]
then
    echo "usage: $0 new_rootfs_dir image_file"
fi

if [ ! -e $mount_root ]
then
    mkdir -pv $mount_root
fi

set -eux

PART=2

PART_OFFSET=$(partx -s $img_file | head -n 3 | tail -n 1 | awk '{print $2}')
PART_OFFSET=$((PART_OFFSET * 512)) # sector size is 512

echo "PART: $PART"
echo "PART OFFSET: $PART_OFFSET"

# some old version fuse2fs not support offset
$THISDIR/fuse2fs -o fakeroot -o offset=$PART_OFFSET $img_file $mount_root

# copy root files
echo "copy root files now"
find $source_dir -mindepth 1 -maxdepth 1 -type d ! -name "boot" -exec cp -r {} $mount_root \;
sync
echo "copy root files done"

# umount
umount $mount_root

echo "copy boot files now"
# Change to source directory
cd "$source_dir/boot" || exit

# Iterate through all files in the source directory
for file in *; do
    # Check if the file is a regular file
    if [ -f "$file" ]; then
        # Copy individual file to the target directory
        mcopy -o -i "$img_file@@1s" "$file" ::/
        echo "Copied $file to $img_file boot partition"
    fi
done

sync
echo "copy boot files done"
```
