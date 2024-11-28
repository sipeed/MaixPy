---
title: Python 基础知识
---

MaixPy 的教程文档里面就不涉及具体的 Python 语法教程了，因为 Python 的教程实在是太多了，都做得很好，这里只介绍需要学什么，方向和线路指导即可。

## Python 简介

Python 是一门解释性、面向对象、动态类型的高级编程语言。
* 解释性：不需要编译，直接运行，优点是开发快速，缺点是因为每次运行都要解释一遍代码，运行速度慢一点点，但是往往瓶颈还是开发者写的代码而不是语言本身。
* 面向对象：支持面向对象编程，可以定义类和对象，相比面向过程语言，更容易组织代码。更多自行搜索。
* 动态类型：变量不需要声明类型，可以直接赋值，类型会根据赋值自动确定，这样可以减少代码量，但是也容易出现类型错误，需要开发者自己注意。

总之，对于没有接触过 Python 的开发者来说，Python 非常容易上手，有大量现成的库，开发者群体巨大，开发应用周期短，非常值得学习！

## Python 环境安装

你可以按照你学习的 Python 教程在电脑上安装 Python；
也可以在 MaixVisioin 上连接设备后使用 MaixVision 编程然后在开发板运行。


## 使用 MaixPy 需要的 Python 基础有哪些？

* Python 的基本概念。
* 面向对象编程的基本概念。
* Python 的基本语法，包括：
  * tab 缩进对齐语法
  * 变量、函数、类、对象、注释等
  * 控制语句比如 if、for、while 等等
  * 模块和导入模块
  * 基本数据类型比如 int、float、str、list、dict、tuple 等等
  * bytes 和 str 的区别和转换
  * 异常处理，try except
  * 常用的内置函数，比如 print、open、len、range 等等
  * 常用的内置模块，比如 os、sys、time、random、math 等等

掌握以上的基础知识就可以顺畅使用 MaixPy 编程了，配合后面的教程和例程，在不懂的时候查询搜索引擎或者官方文档，或者问 ChatGPT 就能顺利完成开发。


## 对于已经有一门面向对象编程语言经验的开发者

如果你已经会一门面向对象语言比如 C++/Java/C# 等等，那只需要快速浏览一下 Python 的语法，就可以开始使用了。

比如 [菜鸟教程](https://www.runoob.com/python3/python3-tutorial.html) 或者 [Python 官方教程](https://docs.python.org/3/tutorial/index.html)。

或者个人开发者的博客，比如 [哇！是 Python](https://neucrack.com/p/59)。

## 对于没有面向对象编程经验但是有 C 语言经验的开发者

如果只学了 C，缺乏对面向对象的理解，那么可以先学习一下面向对象的概念，然后再学习 Python，也是比较快的，可以自行搜索视频教程入门。

跟着视频教程入门之后可以看看文档教程，比如 [菜鸟教程](https://www.runoob.com/python3/python3-tutorial.html) 或者 [Python 官方教程](https://docs.python.org/3/tutorial/index.html) 就可以开动了！

在学了入门知识后，就可以按照 MaixPy 的文档和例程开始使用 MaixPy 编程了。


## 对于编程新手

如果你从未接触过编程，那么你需要重头开始学习 Python，Python 作为入门语言也是比较合适的，具体可以搜一搜视频教程。

在学会了基础语法后，就能按照例程使用 MaixPy 编程了。


## 使用内置的软件包

Python 已经内置了很多常用的软件包和 API，所以遇到什么问题可以搜索`“Python 使用 xxxx"`说不定就能直接能用。
比如常见的 文件、多线程、多进程、网络、系统、算法等等。

举个例子：
对于没有接触过 Python， 只涉略过初级的单片机开发的同学来说，可能会有些疑问为什么文档没有读写 SD/TF 卡的例程：
因为默认就有文件系统跑在 SD/TF 卡上的，只要用 Python 的文件操作 API 就能读写 SD 卡中的文件：
```python
with open("/root/a.txt", "r") as f:
  content = f.read()
  print(content)
```

