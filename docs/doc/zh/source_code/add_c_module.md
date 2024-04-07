---
title: 给 MaixPy 添加一个 C/C++ 模块
---

## 简介

有时候需要高效地执行某个函数， Python 的速度无法满足时，就可以使用 C/C++ 或者其它编译型语言来实现。


## 通用函数封装

如果你想封装的函数实现的功能不依赖 MaixPy 的其它功能，直接使用 Python 使用 C/C++ 添加模块的通用方法，具体方法可以自行百度，比如 ffi， ctype 等
> 欢迎 PR 添加方法

## 如果你的模块还想依赖 MaixPy 的其它基础 API

你需要先学会编译使用 [MaixCDK](https://github.com/sipeed/MaixCDK)， 因为 MaixPy 就是从 MaixCDK 生成的 API， MaixPy 里面有的功能 MaixCDK 里面也有， 然后 。。。TODO
