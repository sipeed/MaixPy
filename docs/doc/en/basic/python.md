---
title: Python Fundamentals
---

The tutorial documentation of MaixPy does not delve into specific Python syntax tutorials because there are already too many excellent Python tutorials available. Here, we only introduce what needs to be learned, provide guidance on directions and paths.

## Introduction to Python

Python is an interpreted, object-oriented, dynamically typed high-level programming language.
* Interpreted: It does not require compilation, runs directly. The advantage is rapid development, while a minor drawback is the slower execution speed due to code interpretation on each run. However, most often, the bottleneck lies in the developer's code rather than the language itself.
* Object-oriented: It can organize data and related operations into classes and objects. MaixPy features such as cameras and displays are represented as objects, so you should know how to create an object and call its methods.
* Dynamically typed: Variables do not need to declare types, can be assigned directly, and the type will be automatically determined based on the assignment. This reduces code volume, but can also lead to type errors, requiring the developer's attention.

In conclusion, for developers unfamiliar with Python, it is very easy to get started as Python offers plenty of ready-to-use libraries, a large developer community, short application development cycles, making it highly worthwhile to learn!

## Python Environment Setup

You can install Python on your computer according to the Python tutorial you are following for learning.
Alternatively, you can connect to a device via MaixVision on MaixVision and then run the program on the development board.

## What Python Basics are Needed to Use MaixPy?

* Basic concepts of Python.
* Basic concepts of object-oriented programming.
* Basic syntax of Python, including:
  * Tab indentation alignment syntax.
  * Variables, functions, classes, objects, comments, etc.
  * Control statements such as if, for, while, etc.
  * Modules and importing modules.
  * Basic data types such as int, float, str, list, dict, tuple, etc.
  * Difference between bytes and str, and conversion.
  * Exception handling, try-except.
  * Common built-in functions like print, open, len, range, etc.
  * Common built-in modules like os, sys, time, random, math, etc.

Once you understand these topics, you can follow the MaixPy tutorials and examples. When you encounter unfamiliar syntax, check the [official Python tutorial](https://docs.python.org/3/tutorial/index.html) and the relevant API documentation first.

## For Developers Experienced in Another Object-Oriented Programming Language

If you are already proficient in an object-oriented language like C++/Java/C#, you simply need to quickly review Python syntax before starting to use it.

You can refer to resources like [Runoob Tutorial](https://www.runoob.com/python3/python3-tutorial.html) or the [Python Official Tutorial](https://docs.python.org/3/tutorial/index.html).

Alternatively, you can explore individual developers' blogs, such as [Wow! It's Python](https://neucrack.com/p/59).

## For Developers with C Language Experience but No Object-Oriented Programming Experience

If you only know C, first use an introductory Python course to learn classes, objects, and exception handling, then continue with MaixPy. The tutorials below are useful written references.

After following introductory video tutorials, you can then refer to documentation tutorials such as [Runoob Tutorial](https://www.runoob.com/python3/python3-tutorial.html) or the [Python Official Tutorial](https://docs.python.org/3/tutorial/index.html) to get started!

Once you have acquired the basic knowledge, you can start using MaixPy for programming based on the documentation and examples.

## For Programming Beginners

If you have never programmed before, complete an introductory Python course covering variables, conditions, loops, functions, and classes before running the MaixPy examples.

After mastering the basic syntax, you will be able to use MaixPy for programming by following examples provided.


### Using Built-in Packages

Python includes modules for files, threads, networking, system operations, and other common tasks. Check the [Python standard library](https://docs.python.org/3/library/index.html) first when you need one of these features. Pure Python code written for a computer can often run on MaixPy as well.

For example:
For those who are new to Python and have only dabbled in basic microcontroller development, they might wonder why there are no examples in the documentation for reading and writing to SD/TF cards. The reason is that a file system is already running on the SD/TF card by default, so you can use Python’s file handling APIs to read and write files directly on the SD card:

```python
with open("/root/a.txt", "r") as f:
  content = f.read()
  print(content)
```
