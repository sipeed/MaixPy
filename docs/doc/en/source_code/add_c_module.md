---
title: Adding a C/C++ Module to MaixPy
---

## Introduction

Sometimes we need to execute a function efficiently, and the speed of Python cannot meet the requirements. In such cases, we can use C/C++ or other compiled languages to implement the function.

## General Function Encapsulation

If the function you want to encapsulate does not depend on other functionalities of MaixPy, you can directly use the general method of adding C/C++ modules with Python, such as ffi, ctype, etc. You can search for relevant methods online.
> Welcome to contribute methods via PR

## If Your Module Needs to Depend on Other Basic APIs of MaixPy

You need to learn how to compile and use [MaixCDK](https://github.com/sipeed/MaixCDK) first, because MaixPy is generated from MaixCDK APIs. Some functionalities in MaixPy are also available in MaixCDK, and then... TODO
