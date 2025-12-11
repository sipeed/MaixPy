#!/bin/bash
# set -x

function help() {
    echo "Usage:  <version> <os_image> <boot_parts_image>"
    echo "    version:              like:v4.12.3"
    echo "    os_image:             like: maixcam2-2025-12-03-maixpy-v4.12.3.img.xz"
    echo "    boot_parts_image:     like: boot_parts_maixcam2-2025-12-03-maixpy-v4.12.3.axp"

}

function check_url_exists() {
    url=$1
    if [ -z "$url" ]; then
        echo "Error: URL is empty."
        return 1
    fi

    wget --spider --quiet $url
    if [ $? -eq 0 ]; then
        return 0
    else
        return 1
    fi
}

function upload_file_to_sourceforge() {
    src=$1
    dst_url=$2
    if [ ! -f "$src" ]; then
        echo "Error: File $src does not exist."
        return 1
    fi

    filename=$(basename "$src")
    check_url="https://sourceforge.net/projects/maixpy-mirror/files/${version}/${filename}"
    if check_url_exists "check_url"; then
        echo "$filename is existed."
        return 0
    fi

    scp -p $src $dst_url

    return 0
}

param_count=$#
case "$param_count" in
    3)
        version=$1
        os_image=$2
        boot_parts_image=$3
        echo "version: $version"
        echo "os_image: $os_image"
        echo "boot_parts_image: $boot_parts_image"
        url="https://sourceforge.net/projects/maixpy-mirror/files/${version}/"
        if ! check_url_exists $url; then
            echo "Error: Url https://sourceforge.net/projects/maixpy-mirror/files/${version} is not exists."
            exit 1
        fi

        upload_url=lxowalle@frs.sourceforge.net:/home/${version}

        echo "Uploading os image..."
        if ! upload_file_to_sourceforge $os_image $upload_url; then
            echo "Error: Upload os image failed."
            exit 2
        fi

        echo "Uploading boot parts image..."
        if ! upload_file_to_sourceforge $boot_parts_image $upload_url; then
            echo "Error: Upload boot parts image failed."
            exit 3
        fi

        echo "success"
        ;;
    *)
        help
        exit 1
        ;;
esac