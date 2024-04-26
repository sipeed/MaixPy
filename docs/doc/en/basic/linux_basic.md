---
title: Basic Knowledge of Linux
---

## Introduction

For beginners just starting out, you can skip this chapter for now and come back to it after mastering the basics of MaixPy development.

The latest MaixPy supports running Linux on the MaixCAM hardware, so the underlying MaixPy development is based on the Linux system. Although Sipeed has done a lot of work for developers with MaixPy, making it possible to enjoy using it without knowledge of the Linux system, there might be situations where some low-level operations are necessary or for the convenience of developers unfamiliar with Linux. In this section, we will cover some basic Linux knowledge.

## Why Linux System is Needed

Specific reasons can be researched individually. Here are a few examples in simplified terms that may not sound too technical but are easy for beginners to understand:
* In microcontrollers, our program is usually a loop, but with Linux, we can run multiple programs simultaneously, each appearing to run independently, where the actual execution is handled by the operating system.
* With a large community of Linux-based developers, required functionalities and drivers can be easily found without the need to implement them from scratch.
* Linux offers a rich set of accompanying software tools for convenient development and debugging. Some Linux common tools not mentioned in this tutorial can theoretically be used as well.

## File System

What is a file system?
* Similar to a computer's file system, Linux manages hardware disks using a file system, making it easy for us to read and write data to the disk.
* For students who have learned about microcontrollers but not familiar with file system development, imagine having a Flash or TF card where data can be read and written through APIs even after power loss. However, Flash has read/write limitations, requiring a program to ensure its longevity. A file system is like a mature program that manages the Flash space and read/write operations. By calling the file system's APIs, we can significantly reduce development work and ensure stability and security with proven programs.

## Transferring Files between Computer and Device (Development Board)

Since the device has Linux and a file system, how do we send files to it?

For MaixPy, we offer MaixVision for file management in future versions. Before that, you can use the following method:

Here we mainly discuss transferring files through the network. Other methods can be explored on your own by searching for "transferring files to Linux":
* Ensure the device and computer are connected to the same local network, for example:
  * When the MaixCAM's USB port is connected to the computer, a virtual network card is created which can be seen in the device manager on the computer, and the device's IP can be found in the device's `Settings -> Device Information`.
  * Alternatively, connect to the same local network on the device through `Settings -> WiFi`.
* Use SCP or SFTP protocols on the computer to transfer files to the device. There are many specific software options and methods, such as:
  * On Windows, you can use WinSCP, FileZilla, or the scp command.
  * On Linux, use FileZilla or the scp command.
  * On Mac, use FileZilla or the scp command.

## Terminal and Command Line

The terminal is a tool for communicating with and operating the Linux system, similar to Windows' `cmd` or `PowerShell`.

For example, we can enter `ssh root@maixcam-xxxx.local` in the Terminal tool on a Windows system with PowerShell or on a Linux system. You can find the specific name in the device's `Settings->Device Information`, which allows us to connect to the device through the terminal (both username and password are `root`).

Then, we can operate the device by entering commands. For instance, the `ls` command can list the files in the current directory of the device, while `cd` is used to switch to a different directory (similar to clicking folders in file management on a computer),

```shell
cd /     # Switch to the root directory
ls       # Display all files in the current directory (root directory)
```

This will display similar content as below:

```shell
bin         lib         media       root        tmp
boot        lib64       mnt         run         usr
dev         linuxrc     opt         sbin        var
etc         lost+found  proc        sys
```

For more command learning, please search for `Linux command line usage tutorials` on your own. This is just to introduce beginners to basic concepts so that when developers mention them, they can understand what they mean.

