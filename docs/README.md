MaixPy documentation
====

Visit online doc: [https://wiki.sipeed.com/maixpy/](https://wiki.sipeed.com/maixpy/)


## Preview locally


* Install doc build tool `teedoc`:
```shell
pip install teedoc -U
```

* Install plugins used by this doc:
```shell
cd MaixPy/docs
teedoc install
```

* Start local preview server:
```shell
teedoc serve
```
Then open `http://127.0.0.1:2333` in your browser.

* To build a offline html doc:
```shell
teedoc build
```
Then you will find HTML docs in `out` directory.

