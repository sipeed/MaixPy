---
title: 给 MaixPy 添加一个 C/C++ 模块
---

## 简介

有时候需要高效地执行某个函数， Python 的速度无法满足时，就可以使用 C/C++ 或者其它编译型语言来实现。


## 通用函数封装

如果你想封装的函数实现的功能不依赖 MaixPy 的其它功能，直接使用 Python 使用 C/C++ 添加模块的通用方法，具体方法可以自行百度，比如 ffi， ctype 等
> 欢迎 PR 添加方法

## 如果你的模块还想依赖 MaixPy 的其它基础 API

**方法一**： 直接修改 MaixPy 固件，参考 [查看 MaixPy API 源码](../basic/view_src_code.md)。

