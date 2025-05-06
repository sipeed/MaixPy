#!/bin/bash

###
#    update_image.sh <xxxx.axp> <builtin_files.tar.xz/builtin_files_dir> <delete_first_files.txt> <out_path> [rootfs_size]
###

set -e

axp_file=$1
builtin_files=$2
delete_first_files=$3
out_path=$4

rootfs_name=ubuntu_rootfs_sparse.ext4
bootfs_name=bootfs.fat32
rootfs_image_size=AUTO
# if rootf_size is not set, use default value
if [ -n "$5" ]; then
    rootfs_image_size=$5
fi

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


rm -rf tmp2

# if builtin_files is a xz or tar.xz file, unzip it to tmp2/builtin_files
if [[ "$builtin_files" == *.tar.xz ]]; then
    echo "Unzipping $builtin_files"
    tar -Jxvf $builtin_files -C tmp2/
    builtin_files=$(basename "$builtin_files" .tar.xz)
elif [[ "$builtin_files" == *.xz ]]; then
    echo "Unzipping $builtin_files"
    unxz $builtin_files -C tmp2/
    builtin_files=$(basename "$builtin_files" .xz)
elif [ -d "$builtin_files" ]; then
    echo "good, builtin_files is a directory"
else
    echo "builtin_files is not a directory or xz/tar.xz file"
    exit 1
fi

# unzip axp_file
echo "Unzipping $axp_file"
mkdir -p tmp2/axp
unzip -q $axp_file -d tmp2/axp
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
file_size=$(stat -c%s tmp2/rootfs.ext4.raw)
rootfs_image_size0=$(($file_size / 1024 / 1024))M
resize_image=0
if [[ $rootfs_image_size == "AUTO" ]]; then
    rootfs_image_size=$rootfs_image_size0
elif [[ $rootfs_image_size0 != "$rootfs_image_size" ]]; then
    echo "will create new image with size $rootfs_image_size"
    resize_image=1
fi

echo "Mounting raw image to tmp2/rootfs"
mkdir -p tmp2/rootfs
if [ $? -ne 0 ]; then
    echo "Failed to create tmp2/rootfs directory"
    exit 1
fi
mount -t ext4 tmp2/rootfs.ext4.raw tmp2/rootfs
echo "Mounting raw image to tmp2/rootfs done"

finish() {
    if [[ -e tmp2/rootfs ]]; then
        echo "Umounting raw rootfs"
        umount tmp2/rootfs
        echo "umount raw rootfs done"
    fi
    exit 1
}
trap finish ERR

echo "Deleting files in $delete_first_files"
# delete first files
while IFS= read -r line; do
    if [ -z $line ]; then
        continue
    elif [ -d "tmp2/rootfs/$line" ]; then
        echo "Deleting directory $line"
        rm -rf tmp2/rootfs/$line
    elif [ -f "tmp2/rootfs/$line" ]; then
        echo "Deleting file $line"
        rm -f tmp2/rootfs/$line
    else
        echo "File or directory $line not found, skip"
    fi
done < "$delete_first_files"

# copy builtin_files rootfs
echo "Copying files from directory $builtin_files"
target_rootfs_path=tmp2/rootfs
if [[ "$resize_image" == "1" ]]; then
    mkdir tmp2/rootfs_new
    cp -r tmp2/rootfs/* tmp2/rootfs_new/
    target_rootfs_path=tmp2/rootfs_new
fi
find $builtin_files -mindepth 1 -maxdepth 1 -type d ! -name "boot" | while read -r dir; do
    cp -r "$dir" "$target_rootfs_path"
done

# copy boot files
if [[ -e ${builtin_files}/boot ]]; then
    echo "Copying boot files from ${builtin_files}/boot..."
    mkdir -p tmp2/bootfs
    mount -o loop,rw tmp2/axp/$bootfs_name tmp2/bootfs
    cp -rf ${builtin_files}/boot/* tmp2/bootfs/
    umount tmp2/bootfs
    echo "Copying boot files done"
fi

# convert raw image to ext4 sparse image
echo "Making sparse rootfs ..."
rm -f tmp2/axp/${rootfs_name}
./make_ext4fs/make_ext4fs -s -l $rootfs_image_size tmp2/axp/${rootfs_name} $target_rootfs_path
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
parent_dir=$(dirname "$out_path")
name=$(basename $out_path)
out_path=$(realpath $parent_dir)/$name
echo "Zipping axp file to $out_path"
mkdir -p $parent_dir
cd tmp2/axp
zip -r $out_path .
cd -
echo "Zip axp file done"

echo "Syncing ..."
sync
echo "All OK"

