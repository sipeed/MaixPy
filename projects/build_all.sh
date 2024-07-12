#!/bin/bash

set -e

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
        maixcdk release -p maixcam
    fi
    mkdir -p ../apps
    cp -r dist/pack/* ../apps
    cd ..
}

rm -rf apps/

for dir in */; do
  if [ -d "$dir" ]; then
    if [[ "${dir}x" != "apps/x" ]]; then
      echo "----- build ${dir} -----"
      build_start "${dir%/}"
      echo "----- build ${dir} done -----"
    fi
  fi
done


