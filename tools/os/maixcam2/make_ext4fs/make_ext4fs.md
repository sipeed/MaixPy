**make_ext4fs** 
	[ -l <len> ] [ -j <journal size> ] [ -b <block_size> ]
    [ -g <blocks per group> ] [ -i <inodes> ] [ -I <inode size> ]
    [ -L <label> ] [ -f ] [ -a <android mountpoint> ]
    [ -S file_contexts ] [ -C fs_config ] [ -T timestamp ]
    [ -z | -s ] [ -w ] [ -c ] [ -J ] [ -o ] [ -v ] [ -B <block_list_file> ]
	<filename> [<directory>]
【主要参数】：
-s： 指定生成稀疏Sparse格式，不指定为raw格式
-l ： 指定分区大小
-T:   时间戳

示例：
``` shell
$ make_ext4fs -s -l 50M rootfs.ext4 ~/sdk/rootfs
```

Creating filesystem with parameters:
    Size: 52428800
    Block size: 4096
    Blocks per group: 32768
    Inodes per group: 3200
    Inode size: 256
    Journal blocks: 1024
    Label: 
    Blocks: 12800
    Block groups: 1
    Reserved block group size: 7
Created filesystem with 11/3200 inodes and 1238/12800 blocks

``` shell
$ file rootfs.ext4
```
rootfs.ext4: Android sparse image, version: 1.0, Total of 12800 4096-byte output blocks in 10 input chunks.



【挂载】
如果是sparse格式，需要先用simg2img转换成raw格式

``` bash?linenums
$ simg2img rootfs.ext4 rootfs.ext4.raw
$ file rootfs.ext4.raw
$ ls -lh
```
rootfs.ext4.raw: Linux rev 1.0 ext4 filesystem data, UUID=57f8f4bc-abf4-655f-bf67-946fc0f9f25b (extents) (large files)
-rw-r--r--  1  jingxiaoping jingxiaoping  16M 7月   1 14:03 rootfs.ext4
-rw-rw-r--  1 jingxiaoping jingxiaoping  96M 7月   1 14:03 rootfs.ext4.raw

把rootfs.ext4.raw挂载到~/mnt/rootfs
``` shell?linenums
$ sudo mount -t ext4 rootfs.ext4.raw ./mnt/rootfs/
$ ls ./mnt/rootfs -l
```
total 96
drwxr-xr-x 2 root root 4096 7月   1 13:53 aixin
drwxr-x--- 2 root root 4096 7月   1 13:53 bin
drwxr-x--- 2 root root 4096 7月   1 13:53 boot
drwxr-x--- 2 root root 4096 7月   1 13:53 dev
drwxr-x--- 4 root root 4096 7月   1 13:53 etc
drwxr-x--- 2 root root 4096 7月   1 13:53 home
lrwxrwxrwx 1 root root    9 7月   1 13:53 init -> sbin/init
drwxr-x--- 2 root root 4096 7月   1 13:53 komod
drwxr-x--- 2 root root 4096 7月   1 13:53 lib
drwxr-x--- 2 root root 4096 7月   1 13:53 lib64
lrwxrwxrwx 1 root root   11 7月   1 13:53 linuxrc -> bin/busybox
drwxr-x--- 2 root root 4096 7月   1 13:53 lost+found
-rwxr-x--- 1 root root 1317 7月   1 13:53 mkimg.rootfs
-rwxr-x--- 1 root root  431 7月   1 13:53 mknod_console
drwxr-x--- 2 root root 4096 7月   1 13:53 mnt
drwxr-x--- 2 root root 4096 7月   1 13:53 nfsroot
drwxr-x--- 2 root root 4096 7月   1 13:53 opt
drwxr-x--- 2 root root 4096 7月   1 13:53 proc
drwxr-x--- 2 root root 4096 7月   1 13:53 root
dr-xr-x--- 2 root root 4096 7月   1 13:53 sbin
drwxr-x--- 2 root root 4096 7月   1 13:53 share
drwxr-x--- 2 root root 4096 7月   1 13:53 sharefs
drwxr-x--- 2 root root 4096 7月   1 13:53 sys
drwxr-x--- 2 root root 4096 7月   1 13:53 tmp
drwxr-x--- 6 root root 4096 7月   1 13:53 usr
drwxr-x--- 3 root root 4096 7月   1 13:53 var

umount

``` shell
$ df -T
```
/dev/loop17    ext4          92656     10732      79960  12% /home/jingxiaoping/mnt/rootfs

``` shell
$ sudo umount /dev/loop17
```

