#!/bin/bash

set -e


#############################################
# 定义不同平台的黑名单

blacklist_linux=()
blacklist_maixcam=("app_yoloworld" "app_vlm" "app_mono_depth_estimation")
blacklist_maixcam2=("app_mouse_simulator")

#############################################

platform=""

function platform_setting()
{
    echo "----------------------------------"
    echo "          Platform Setting:        "
    echo "----------------------------------"
    echo "Current platform: ${platform}"
    echo "1. linux"
    echo "2. maixcam"
    echo "3. maixcam2"
    echo "----------------------------------"
	read -p "Select your platform [1-3]: " choice
	case "$choice" in
		1)
			platform="linux"
	    ;;
		2)
			platform="maixcam"
	    ;;
		3)
			platform="maixcam2"
	    ;;
		*)
			echo "Select platform failed"
			exit 1
	    ;;
	esac
}

function build_start()
{
    # test_script $1
    # if [ $? -ne 0 ]; then
    #     echo "Error: $1 failed to execute."
    #     exit 1
    # fi
    cd $1
    if [[ -f main.py ]]; then
        rm -rf dist
        maixtool release
    else
        maixcdk distclean
        maixcdk release -p "$platform" --toolchain-id default
    fi
    mkdir -p ../apps
    cp -r dist/pack/* ../apps
    cd ..
}

if [ -n "$1" ]; then
    platform="$1"
else
    platform_setting
fi

# 获取当前平台对应的黑名单数组
blacklist_var="blacklist_${platform}[@]"
blacklist=("${!blacklist_var}")

rm -rf apps/

for dir in */; do
  if [ -d "$dir" ]; then
    if [[ $dir == app* && $dir != apps* ]]; then

      # 检查是否在黑名单
      skip=false
      for b in "${blacklist[@]}"; do
        if [[ "$dir" == "$b/" ]]; then
          echo "skip $dir for $platform"
          skip=true
          break
        fi
      done

      if $skip; then
        continue
      fi

      echo "----- build ${dir} -----"
      build_start "${dir%/}"
      echo "----- build ${dir} done -----"
    fi
  fi
done


