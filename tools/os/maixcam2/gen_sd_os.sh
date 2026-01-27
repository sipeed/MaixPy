#!/bin/bash

# ==================================================
# 脚本功能：将镜像打包为SD卡镜像
# 注意： 本脚本依赖于./gen_os.sh生成的文件， 请先运行./gen_os.sh后再执行本脚本
# boot启动文件sd_boot_pack需要从MaixCAM2_AX630C_SDK打包镜像时获取， 见MaixCAM2_AX630C_SDK/README.md
# bootfs.fat32是运行gen_os.sh后生成的tmp/axp/bootfs.fat32
# rootfs是运行gen_os.sh后生成的tmp/axp/ubuntu_rootfs_sparse.ext4
# ==================================================

set -e
# set -x

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印彩色消息
print_error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

print_success() {
    echo -e "${GREEN}[OK] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

print_info() {
    echo -e "${GREEN}[INFO] $1${NC}"
}

# Show help messages
show_help() {
    echo "Usage: $0 [options] [params]"
    echo ""
    echo "Options:"
    echo "  -d, --device                Specify the SD card device path (e.g. /dev/sdb)"
    echo "  --maixpy-version            MaixPy version (e.g. v4.12.4)"
    echo "  --bootfs                    Boot filesystem file (e.g. bootfs.fat32)"
    echo "  --rootfs                    Root filesystem path (e.g. ubuntu_rootfs_sparse.ext4)"
    echo "  --sd_boot_dir               SD boot path (e.g. sd_boot_pack)"
    echo "                              sd_boot_pack must includes: atf.img  dtb.img  kernel.img  uboot.bin boot.bin"
    echo "                              Note: boot.bin is the same as spl_AX630C_emmc_arm64_k419_xxx_xxx_sd_signed.bin"
    echo "  --disable_rootfs_simg2img   Dsiable rootfs simg2img"
    echo "  --disable_dd_new_image      Dsiable create a new image"
    echo "  --disable_compress_image    Dsiable compress image"
    echo "  -h, --help        Show help messages"
    echo ""
    echo "Examples:"
    echo "  $0 --sd_boot_dir build/sd_boot_pack --bootfs tmp2/axp/bootfs.fat32 --rootfs tmp2/axp/ubuntu_rootfs_sparse.ext4 --maixpy-version v4.12.4"
    echo "  $0 --disable_rootfs_simg2img --disable_dd_new_image --disable_compress_image --sd_boot_dir build/sd_boot_pack --bootfs tmp2/axp/bootfs.fat32 --rootfs tmp2/axp/ubuntu_rootfs_sparse.ext4 --maixpy-version v4.12.4"
    echo ""
    echo "Important:"
    echo "  1. This script requires root permission."
}

# Check command exists
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "Unknown command: $1"
        exit 1
    fi
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script need root permission!!"
        exit 1
    fi
}

# Check exists
check_exists() {
    local file=$1

    if [[ ! -e $file ]]; then
        print_error "$file is not exist"
        exit 1
    fi
}

# Check block device
check_device() {
    local device=$1

    if [[ ! -b $device ]]; then
        print_error "Device $device is not exist or not a block device"
        exit 1
    fi
}

# Check device is mounted
check_mounted() {
    local device=$1

    if mount | grep -q "^$device"; then
        print_warning "Device $device is mounted, Try to unmount..."

        # 卸载所有相关分区
        for part in ${device}[0-9]*; do
            if [[ -b $part ]] && mountpoint -q ${part}; then
                umount $part 2>/dev/null && print_info "$part unmounted" || true
            fi
        done

        # 再次检查
        sleep 1
        if mount | grep -q "^$device"; then
            print_error "Can not mount device $device, please unmount manually"
            exit 1
        fi
    fi
}

# Get device info
get_device_info() {
    local device=$1

    echo ""
    print_info "=== Device Info ==="

    # Show device info
    fdisk -l $device | grep -E "(Disk|磁盘|大小)"

    # Show partition table
    print_info "Current partition table:"
    fdisk -l $device | grep -A 100 -E "(Device|设备)" || echo 0
}

# Confirm operation
confirm_operation() {
    local device=$1
    local first_size=$2
    local second_size=$3

    echo ""
    print_warning "We will perform the following operations on device $device:"
    echo "  1. Delete all partitions"
    echo "  2. Create first partition: $((first_size/1024/1024))MB FAT32"
    echo "  3. Create second partition: $((second_size/1024/1024))MB ext4"
    echo ""
    print_warning "It will delete all data on device $device"

    # read -p "Continue? (y/N): " -n 1 -r
    # echo
    # if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    #     print_info "Operation cancelled"
    #     exit 0
    # fi
}

# Clear old partition table
wipe_partition_table() {
    local device=$1

    print_info "Clear partition table..."

    # Use wipefs to clear file system signatures
    wipefs -a $device

    # Clear old MBR/GPT
    dd if=/dev/zero of=$device bs=1M count=1 2>/dev/null
    sync

    print_success "Partition table cleared"
}

align_to_sector() {
    local bytes=$1
    local SECTOR_SIZE=512
    echo $(( (bytes + SECTOR_SIZE - 1) / SECTOR_SIZE * SECTOR_SIZE ))
}

# Use parted to create partitions
create_partitions_parted() {
    local device=$1
    local first_start=$((1048576))
    local first_size_bytes=$2
    local first_end=$((first_start+first_size_bytes))
    local second_size_bytes=$3
    local second_start=$((first_end))
    local second_end=$((first_end + $second_size_bytes))

    second_start=$((second_start + first_start))

    print_info "Use parted to create partitions"

    print_info "make label msdos"
    parted -s $device mklabel msdos

    print_info "create partition 1, start:${first_start} end:${first_end} size: $((first_size_bytes/1024/1024))MB"
    parted -s $device mkpart primary fat32 ${first_start}B ${first_end}B
    # parted -s $device set 1 esp on  # 设置ESP标志（可选）

    print_info "create partition 2, start:${second_start} end:${second_end} size: $((second_size_bytes/1024/1024))MB"
    parted -s $device mkpart primary ext4 ${second_start}B ${second_end}B

    parted -s $device align-check optimal 1
    parted -s $device align-check optimal 2

    print_success "Partition table created"
}

# 使用 fdisk 创建分区（备选）
create_partitions_fdisk() {
    local device=$1
    local second_size_gb=$2

    print_info "使用 fdisk 创建分区..."

    # 创建分区表并分区
    fdisk $device << EOF
g
n


+128M
n



t
1
1
w
EOF

    print_success "分区创建完成"
}

# 格式化分区
format_partitions() {
    local device=$1

    print_info "格式化分区..."

    # 等待内核重新读取分区表
    partprobe $device

    sleep 1

    # 格式化第一个分区为FAT32
    if [[ -b ${device}p1 ]]; then
        print_info "Formatting ${device}p1 to FAT32..."
        mkfs.vfat -F 32 -n "BOOT" ${device}p1
        print_success "FAT32 formatting complete"
    else
        print_error "${device}p1 is not exist"
        exit 1
    fi

    # 格式化第二个分区为ext4
    if [[ -b ${device}p2 ]]; then
        print_info "Formatting ${device}p1 to ext4..."
        mkfs.ext4 -F -L "ROOTFS" ${device}p2
        print_success "ext4 formatting complete"
    else
        print_error "Partition ${device}p2 is not exist"
        exit 1
    fi
}

# 显示最终结果
show_result() {
    local device=$1

    echo ""
    print_success "=== 分区完成 ==="
    print_info "设备 $device 已成功分区："
    echo ""

    # 显示分区表
    fdisk -l $device

    echo ""
    print_info "分区信息摘要："
    lsblk -f $device

    echo ""
    print_info "你可以使用以下命令挂载分区："
    echo "  sudo mount ${device}1 /mnt/boot"
    echo "  sudo mount ${device}2 /mnt/rootfs"
}

# 主函数
main() {
    # 默认参数
    local DEVICE=""
    local SD_BOOT_PATH=""
    local BOOTFS_PATH=""
    local ROOTFS_PATH=""
    local ROOTFS_RAW_PATH="tmp2/ubuntu_rootfs_raw.ext4"
    local FIRST_SIZE=134217728     # unit:Bytes
    local SECOND_SIZE=0     # unit:Bytes
    local MAIXPY_VERSION="v4.12.4"
    local IMG_PATH=""
    local DISABLE_ROOTFS_SIMG2IMG=0
    local DISABLE_DD_NEW_IMAGE=0
    local DISABLE_COMPRESS_IMAGE=0

    # 检查必需的命令
    check_command "fdisk"
    check_command "parted"
    check_command "mkfs.vfat"
    check_command "mkfs.ext4"
    check_command "wipefs"
    check_command "lsblk"
    check_command "p7zip"

    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -d|--device)
                DEVICE=$2
                shift 2
                ;;
            --maixpy-version)
                MAIXPY_VERSION=$2
                shift 2
                ;;
            --bootfs)
                BOOTFS_PATH=$2
                shift 2
                ;;
            --rootfs)
                ROOTFS_PATH=$2
                shift 2
                ;;
            --sd_boot_dir)
                SD_BOOT_PATH=$2
                shift 2
                ;;
            --disable_rootfs_simg2img)
                DISABLE_ROOTFS_SIMG2IMG=1
                shift
                ;;
            --disable_dd_new_image)
                DISABLE_DD_NEW_IMAGE=1
                shift
                ;;
            --disable_compress_image)
                DISABLE_COMPRESS_IMAGE=1
                shift
                ;;
            *)
                print_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # 检查设备参数
    if [[ -z $MAIXPY_VERSION ]]; then
        print_error "Please specify --maixpy-version param!"
        show_help
        exit 1
    fi

    if [[ -z $SD_BOOT_PATH ]]; then
        print_error "Please specify --sd_boot_dir param!"
        show_help
        exit 1
    fi

    if [[ -z $BOOTFS_PATH ]]; then
        print_error "Please specify --bootfs param!"
        show_help
        exit 1
    fi

    if [[ -z $ROOTFS_PATH ]]; then
        print_error "Please specify --rootfs_dir param!"
        show_help
        exit 1
    fi

    check_exists "$SD_BOOT_PATH"
    check_exists "$BOOTFS_PATH"
    check_exists "$ROOTFS_PATH"
    check_root
    umount tmp2/sd/sd_boot &> /dev/null || echo ""
    umount tmp2/sd/sd_rootfs &> /dev/null || echo ""
    umount tmp2/sd/ubuntu_rootfs &> /dev/null || echo ""
    umount tmp2/sd/bootfs &> /dev/null || echo ""
    print_info "Converting $ROOTFS_PATH to $ROOTFS_RAW_PATH..."
    if [ $DISABLE_ROOTFS_SIMG2IMG -eq 1 ]; then
        print_warning "Skip convert $ROOTFS_PATH to $ROOTFS_RAW_PATH..."
    else
        if [ -f $ROOTFS_RAW_PATH ]; then
            rm $ROOTFS_RAW_PATH
        fi
        simg2img $ROOTFS_PATH $ROOTFS_RAW_PATH
    fi
    check_exists "$ROOTFS_RAW_PATH"

    BOOT_SIZE=$(stat -c %s $BOOTFS_PATH)
    ROOTFS_SIZE=$(stat -c %s $ROOTFS_RAW_PATH)
    SECOND_SIZE=$((BOOT_SIZE + ROOTFS_SIZE))
    if [[ -z $DEVICE ]]; then
        datetime=$(date "+%Y-%m-%d")
        IMG_PATH="images/maixcam2-${datetime}-maixpy-${MAIXPY_VERSION}_sd.img"
        print_info "create a new image($IMG_PATH)..."
        if [ $DISABLE_DD_NEW_IMAGE -eq 1 ]; then
            print_warning "Skip create image..."
        else
            mkdir -p images
            rm -f $IMG_PATH
            dd if=/dev/zero of=$IMG_PATH bs=1M count=$(((FIRST_SIZE+SECOND_SIZE)/1024/1024 + 128))
        fi
        check_exists $IMG_PATH
        losetup -d $IMG_PATH || echo 0
        DEVICE="$(losetup -f --show $IMG_PATH)"
    fi

    check_device "$DEVICE"
    check_mounted "$DEVICE"
    get_device_info "$DEVICE"

    echo "DEVICE:" $DEVICE
    echo "SD_BOOT_PATH:" $SD_BOOT_PATH
    echo "BOOTFS_PATH:" $BOOTFS_PATH "SIZE:" $(expr $FIRST_SIZE / 1024 / 1024) "MB"
    echo "ROOTFS_PATH:" $ROOTFS_RAW_PATH "SIZE:" $(expr $SECOND_SIZE / 1024 / 1024) "MB"

    # Execute partition operations
    confirm_operation "$DEVICE" "$FIRST_SIZE" "$SECOND_SIZE"
    wipe_partition_table "$DEVICE"
    create_partitions_parted "$DEVICE" "$FIRST_SIZE" "$SECOND_SIZE"
    format_partitions "$DEVICE"

    print_info "Mounting partitions..."
    mkdir -p tmp2/sd/sd_boot tmp2/sd/sd_rootfs
    mount "${DEVICE}p1" tmp2/sd/sd_boot            # mount /dev/sdb1
    mount "${DEVICE}p2" tmp2/sd/sd_rootfs          # mount /dev/sdb2

    print_info "Mounting loop devices..."
    mkdir -p tmp2/sd/ubuntu_rootfs tmp2/sd/bootfs
    mount -o loop $BOOTFS_PATH tmp2/sd/bootfs
    mount -o loop $ROOTFS_RAW_PATH tmp2/sd/ubuntu_rootfs

    print_info "Copying sd_boot_pack files..."
    cp $SD_BOOT_PATH/* tmp2/sd/sd_boot

    print_info "Copying bootfs files..."
    cp -r tmp2/sd/bootfs/* tmp2/sd/sd_boot

    print_info "Copying ubuntu_rootfs files..."
    cp -r tmp2/sd/ubuntu_rootfs/* tmp2/sd/sd_rootfs

    print_info "Unmounting..."
    sleep 2
    umount tmp2/sd/sd_boot &> /dev/null || echo ""
    umount tmp2/sd/sd_rootfs &> /dev/null || echo ""
    umount tmp2/sd/ubuntu_rootfs &> /dev/null || echo ""
    umount tmp2/sd/bootfs &> /dev/null || echo ""
    losetup -d $DEVICE &> /dev/null || echo ""

    print_info "Compressing sd.img..."
    if [ $DISABLE_COMPRESS_IMAGE -eq 1 ]; then
        print_warning "Skip compress image..."
    else
        7z a -v2g -mx9 $IMG_PATH.7z $IMG_PATH
    fi

    print_success "All done!"
}

# 捕获信号（Ctrl+C）
trap 'echo -e "\n${YELLOW}[警告] 操作被用户中断${NC}"; exit 1' INT

# 运行主函数
main "$@"