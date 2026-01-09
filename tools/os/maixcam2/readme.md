# README

这个目录存放打包MaixCAM2的工具

## 打包镜像
1. 创建`build`目录
```shell
cd ~/MaixPy/tools/os/maixcam2
mkdir build
```
2. 获取MaixCAM2的基础镜像，通过仓库[maix_ax620e_sdk](https://github.com/sipeed/maix_ax620e_sdk)编译出基础镜像(例如：`AX630C_emmc_arm64_k419_sipeed_maixcam2_ubuntu_rootfs_V3.0.0_xxx_glibc.axp`)，将`xxx.axp`拷贝到`build`目录下
```shell
cp maix_ax620e_sdk/build/out/AX630C_emmc_arm64_k419_sipeed_maixcam2_ubuntu_rootfs_V3.0.0_xxx_glibc.axp build
```

3. 编译`MaixPy`并将输出的`.whl`包拷贝到`build`目录下
```shell
cd ~/MaixPy
python setup.py bdist_wheel maixcam2
cp ~/MaixPy/dist/maixpy-xxx-cp313-cp313-manylinux2014_aarch64.whl ~/MaixPy/tools/os/maixcam2/build
```

4. 获取`maixcam2_builtin_files`(目前没有对外提供)并放到`build`目录下
```shell
cp -r ~/maixcam2_builtin_files build
```

5. 运行打包脚本
```shell
/gen_os.sh maix_ax620e_sdk/build/out/AX630C_emmc_arm64_k419_sipeed_maixcam2_ubuntu_rootfs_V3.0.0_xxx_glibc.axp build/maixpy-xxx-cp313-cp313-manylinux2014_aarch64.whl build/maixcam2_builtin_files/maixcam2_builtin_files 1 maixcam2
```

## 打包SD卡镜像

一定要先打包一次镜像，然后才能打包SD卡镜像

1. 获取`sd_boot_pack`，获取方法见仓库[maix_ax620e_sdk](https://github.com/sipeed/maix_ax620e_sdk)的readme说明
获取`sd_boot_pack`并拷贝到`build`目录下， `sd_boot_pack`路径:`maix_ax620e_sdk/build/out/AX630C_emmc_arm64_k419_sipeed_xxx/images/sd_boot_pack`下
获取`spl_AX630C_emmc_arm64_k419_sipeed_xxx_sd_signed.bin`并重命名`boot.bin`后放到`build`目录下，`spl_AX630C_emmc_arm64_k419_sipeed_xxx_sd_signed.bin`位于`maix_ax620e_sdk/build/out/AX630C_emmc_arm64_k419_sipeed_xxx/images/spl_AX630C_emmc_arm64_k419_sipeed_xxx_sd_signed.bin`
```shell
# 拷贝maix_ax620e_sdk编译出的sd_boot_pack到build目录下
cp -r maix_ax620e_sdk/build/out/AX630C_emmc_arm64_k419_sipeed_xxx/images/sd_boot_pack ~/MaixPy/tools/os/maixcam2/build

# 拷贝maix_ax620e_sdk编译出的spl_AX630C_emmc_arm64_k419_sipeed_xxx_sd_signed.bin到build目录下，并重命名为boot.bin
cp maix_ax620e_sdk/build/out/AX630C_emmc_arm64_k419_sipeed_xxx/images/spl_AX630C_emmc_arm64_k419_sipeed_xxx_sd_signed.bin ~/MaixPy/tools/os/maixcam2/build/sd_boot_pack/boot.bin
```

2. 运行打包SD卡镜像脚本
```shell
# tmp2/axp/bootfs.fat32和tmp2/axp/ubuntu_rootfs_sparse.ext4 文件是在打包镜像时生成的
./gen_sd_os.sh --sd_boot_dir build/sd_boot_pack --bootfs tmp2/axp/bootfs.fat32 --rootfs tmp2/axp/ubuntu_rootfs_sparse.ext4 --maixpy-version v4.12.5
```