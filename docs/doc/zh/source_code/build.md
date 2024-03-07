---
title: MaixPy develop source code guide
---


## Build

```shell
maixcdk build
```
And if add or delete files, run `maixcdk rebuild`.

## Run test after modify source code

* First, build source code by
```shell
maixcdk build
```

* Then go to `test` directory, execute `./run.sh your_test_file_name.py` to run python script.
```shell
cd test
./run.sh test_image.py
```

## Pack to wheel


```shell
python setup.py bdist_wheel linux
```
`linux` Can be replaced with other board config, see [configs](./configs) directory

> `python setup.py bdist_wheel linux --not-clean` will not execute distclean command, so you can use `maixcdk build` first to customize building.

After build success, you will find wheel file in dist directory, use `pip install -U MaixPy****.wheel` on you board to install or upgrade.


## Documentation

Documentation in [docs][./docs] directory, use `Markdown` format, you can use [teedoc](https://github.com/teedoc/teedoc) to generate web version documentation.

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
