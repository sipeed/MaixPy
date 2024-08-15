---
title: MaixCAM MaixPy develop source code guide
---

## Get source code

```shell
mkdir -p ~/maix
cd ~/maix
git clone https://github.com/sipeed/MaixPy
```

## Getting MaixCDK Source Code

The MaixPy project depends on MaixCDK. You need to clone it first and place it in a directory on your computer (do not place it under the MaixPy directory).

```shell
cd ~/maix
git clone https://github.com/sipeed/MaixCDK
```

Then, you need to set the environment variable MAIXCDK_PATH to specify the path to MaixCDK, which can be added in ~/.bashrc or ~/.zshrc (depending on your shell):

```shell
export MAIXCDK_PATH=~/maix/MaixCDK
```

Only after successfully setting the environment variable can MaixPy locate the MaixCDK source code.


## Build and pack to wheel

```shell
cd ~/maix/MaixPy
python setup.py bdist_wheel maixcam
```

`maixcam` Can be replaced with other board config, see [setup.py]([./configs](https://github.com/sipeed/MaixPy/blob/main/setup.py)) 's `platform_names` variable.


After build success, you will find wheel file in `dist` directory, use `pip install -U MaixPy****.whl` on your device to install or upgrade.

> `python setup.py bdist_wheel maixcam --skip-build` will not execute build command and only pack wheel, so you can use `maixcdk menuconfig` and `maixcdk build` first to customize building.

> Additionally, if you are debugging APIs and need to install frequently, using pip can be slow. You can compile and then copy the maix directory directly to the /usr/lib/python3.11/site-packages directory on your device to overwrite the old files.


## Build manually

```shell
maixcdk build
```

## Run test after modify source code

* First, build source code by
```shell
maixcdk build
```

* If build for PC self(platform `linux`):
Then execute `./run.sh your_test_file_name.py` to run python script.
```shell
cd test
./run.sh examples/hello_maix.py
```

* If cross compile for board:
  * The fastest way is copy `maix` dir to device's `/usr/lib/python3.11/site-packages/` directory, then run script on device.
  * Or pack wheel and install on device by `pip install -U MaixPy****.whl`, then run script on device.

## Preview documentation locally

Documentation in [docs](https://github.com/sipeed/MaixPy/tree/main/docs) directory, use `Markdown` format, you can use [teedoc](https://github.com/teedoc/teedoc) to generate web version documentation.

And the API doc is generated when build MaixPy firmware, **if you don't build MaixPy, the API doc will be empty**.

```shell
pip install teedoc -U
cd docs
teedoc install -i https://pypi.tuna.tsinghua.edu.cn/simple
teedoc serve
```

Then visit `http://127.0.0.1:2333` to preview documentation on web browser.


## For developers who want to contribute

See [MaixPy develop source code guide](./contribute.md)

If you encounter any problems when use source code, please refer to [FAQ](./faq.md) first.

