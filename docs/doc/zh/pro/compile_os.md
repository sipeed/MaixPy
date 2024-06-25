---
title: 为 MaixCAM 编译系统
---

## 定制和编译系统

你可以从 [https://github.com/sipeed/MaixPy/releases](https://github.com/sipeed/MaixPy/releases) 下载到适合 MaixCAM 的最新系统。

你可以从 [https://github.com/sipeed/LicheeRV-Nano-Build/releases](https://github.com/sipeed/LicheeRV-Nano-Build/releases)下载到最新的基础系统（不能直接给 MaixCAM 烧录使用，否则有烧坏屏幕风险）。

系统源码和编译请参考 [https://github.com/sipeed/LicheeRV-Nano-Build](https://github.com/sipeed/LicheeRV-Nano-Build)，尽量用 readme 提到的 docker 编译以避免遇到编译问题（注意编译出来的系统不能直接给 MaixCAM 烧录使用，否则有烧坏屏幕风险）。


## 为 MaixCAM 拷贝文件

编译通过后会得到一个 img 文件，对于 MaixCAM 还需要放一些额外的文件进去，下载[压缩包](https://github.com/sipeed/MaixPy/releases/download/v4.3.2/sys_builtin_files_2024.6.19.tar.xz)，解压后将附录中的脚本保存成`update_img.sh`， 复制一份`img`， 然后执行`./update_img.sh sys_builtin_files_路径 复制的_img_路径`，这个 `img` 就能用来烧录给 MaixCAM 使用了。

不过需要注意，这里的压缩包是 `v4.3.2` 版本的，不是最新的版本，根据你自己的情况合理删减里面的内容即可，以及 MaixPy 在`usr/lib`目录下，也可以手动更新。


## 附录 `update_img.sh`：

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
```
