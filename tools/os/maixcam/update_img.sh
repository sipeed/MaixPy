#!/bin/bash

set -e
set -o pipefail

source_dir=$1
img_file=$2
delete_first_files=$3
mount_root=img_root

img_file=$(readlink -f "$img_file")
THISDIR=$(dirname $(realpath $0))

if [ -z $img_file ]
then
	echo "usage: $0 new_rootfs_dir image_file"
fi

if [ ! -f "$delete_first_files" ]; then
    echo "File $delete_first_files not found!"
    exit 1
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

echo "Deleting files in $delete_first_files"
# delete first files
while IFS= read -r line; do
    if [ -z $line ]; then
        continue
    elif [ -d "$mount_root/$line" ]; then
        echo "Deleting directory $line"
        rm -rf $mount_root/$line
    elif [ -f "$mount_root/$line" ]; then
        echo "Deleting file $line"
        rm -f $mount_root/$line
    else
        echo "File or directory $line not found, skip"
    fi
done < "$delete_first_files"

# copy root files
echo "copy root files now"
find $source_dir -mindepth 1 -maxdepth 1 -type d ! -name "boot" | while read -r dir; do
    cp -r "$dir" "$mount_root"
done
sync
echo "copy root files done"

# umount
umount $mount_root
rm -rf $mount_root


echo "copy boot files now"
# 切换到源目录
cd "$source_dir/boot" || exit

# 遍历源目录中的所有文件
for file in *; do
    # 检查文件是否为普通文件
    if [ -f "$file" ]; then
        # 拷贝单个文件到目标目录
        mcopy -o -i "$img_file@@1s" "$file" ::/
        echo "Copied $file to $img_file boot partition"
    fi
done

sync
echo "copy boot files done"


