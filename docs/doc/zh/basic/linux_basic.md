---
title: Linux 基础知识
update:
  - date: unknown
    author: unknown 
    version: 1.0.0
    content: 初版文档
  - date: 2024-10-26
    author: YWJ
    version: 2.0.0
    content: 跟新文档部分内容
---

## 简介

本章内容对于刚入门的同学来说，可以先跳过此章节，在学会 MaixPy 基础开发后再来学习也是可以的。

最新的 MaixPy 支持的 MaixCAM 硬件支持跑 Linux 系统，所以 MaixPy 底层都是基于 Linux 系统进行开发的。
虽然 Sipeed 开发的 MaixPy 已经为开发者们做了很多工作，即使不知道 Linux 系统知识也能愉快使用，但是以防在某些情况下需要一些底层操作，以及方便未接触过 Linux 的开发者学习，这里写一些 Linux 基础知识。


## 为什么需要 Linux 系统

具体的原因大家可以自行查阅，这里用通俗的看起来不太专业的话语简单举几个例子方便初学者理解：
* 在单片机中，我们的程序是一个死循环程序，用上 Linux 后我们可以同时跑很多程序，每个程序看起来都独立在同时运行，每个程序具体怎么执行的由操作系统实现。
* 基于 Linux 的开发者众多，需要功能和驱动可以很方便地找到，不需要自己再实现一遍。
* 基于 Linux 配套的软件工具丰富，可以很方便地进行开发和调试，比如在本教程没有提到的一些 Linux 通用工具理论上也是可以使用的。


## 文件系统

什么是文件系统？
* 就像电脑的文件系统一样，Linux 上会将硬件磁盘用文件系统进行管理，这样我们可以很方便地向磁盘读写数据。
* 对于学过单片机没有接触过文件系统开发的同学来讲，可以理解为我们有一个 Flash 或者 TF 卡，我们可以通过 API 读写 Flash 存取数据，断电后也能保存数据，但是 Flash 具有读写寿命，我们往往需要写一套程序去保证 Flash 读写寿命，而文件系统就可以理解成这样一套成熟的程序，文件系统帮我们完成了具体如何管理 Flash 空间和读写，我们只需调用文件系统的 API 即可，大大减少了我们的开发工作量并且用成熟的程序保证了稳定性和安全性。

## 在电脑和设备（开发板）之间传输文件

既然设备有 Linux 和文件系统，那我们怎么发送文件到设备呢？

对于 MaixPy 我们配套了 MaixVision， 在后面的版本也会支持文件管理功能，在此之前可以用下面的方法：

这里我们主要介绍通过网络传输的方式，其它方式可自行探索`传输文件到 Linux`：
* 确保设备和电脑连接到了同一个局域网，比如：
  * MaixCAM 的 USB 口连接到电脑会创建一个虚拟网卡，在电脑端的设备管理器就能看到，设备的 IP 可以在设备的`设置->设备信息`中看到设备名和 IP。
  * 也可以在设备`设置->WiFi`中连接到和电脑相同的局域网。
* 电脑使用 SCP 或者 SFTP 协议传输文件到设备，具体的软件有很多，具体的软件和使用方法可以自行搜索，比如：
  * 在 Windows 上可以使用 WinSCP 或者 FileZilla，或者 scp 命令等。
  * 在 Linux 上可以使用 FileZilla 或者 scp 命令 等。
  * 在 Mac 上可以使用 FileZilla 或者 scp 命令 等。


## 终端和命令行

终端就是通过`终端`这个软件与 Linux 系统进行通信和操作的工具，类似于 Windows 的`cmd`或者`PowerShell`。

比如我们可以在电脑的 Window 系统中的 powershell 或者 Linux系统中的 终端 工具中输入`ssh root@maixcam-xxxx.local` 这里具体的名字在设备的`设置->设备信息`中可以看到，这样我们就可以通过终端连接到设备了(用户名和密码都是`root`)。
然后我们通过输入命令来操作设备，比如`ls`命令可以列出设备文件系统中当前目录下的文件, `cd` 用来切换当前所在的目录（就像电脑文件管理中点击文件夹切换目录一样），
```shell
cd /     # 切换到根目录
ls       # 显示当前目录（根目录）下的所有文件
```
然后会显示类似下面的内容：
```shell
bin         lib         media       root        tmp
boot        lib64       mnt         run         usr
dev         linuxrc     opt         sbin        var
etc         lost+found  proc        sys
```

更多命令学习请自行搜索`Linux 命令行使用教程`，这里只是为了让初学者知道基本概念，这样有开发者提到时可以知道是什么意思。


### Linux 基础知识详解版

#### 一、Linux简介

**1. 什么是Linux？**

Linux是一个开源的、类Unix的操作系统，由Linus Torvalds在1991年首次发布。它基于POSIX标准，是一个多用户、多任务、支持多线程和多CPU的操作系统。Linux的内核是自由和开放源码的，任何人都可以自由使用、修改和分发。

**2. Linux的特点**

- **开源性**：Linux的源代码是公开的，任何人都可以查看、修改和分发。
- **多用户多任务**：Linux支持多个用户同时登录和运行多个任务。
- **安全性**：Linux具有强大的权限管理和用户隔离机制，安全性较高。
- **稳定性**：Linux系统稳定性高，适合长时间运行。
- **兼容性**：Linux支持多种硬件平台，包括x86、ARM、PowerPC等。

**3. Linux的发行版**

Linux有众多发行版，常见的包括：
- **Ubuntu**：基于Debian，适合桌面和服务器使用。
- **CentOS**：基于Red Hat Enterprise Linux，适合服务器使用。
- **Debian**：稳定性高，适合服务器和桌面使用。
- **Fedora**：由Red Hat赞助，适合开发和桌面使用。
- **Arch Linux**：滚动更新，适合高级用户。

#### 二、Linux的基本操作

**1. 文件和目录操作**

- **ls**：列出目录内容。
  ```bash
  ls -l  # 详细列表
  ls -a  # 显示隐藏文件
  ```

- **cd**：改变当前目录。
  ```bash
  cd /home/user  # 进入/home/user目录
  cd ..  # 返回上一级目录
  cd ~  # 返回用户主目录
  ```

- **pwd**：显示当前工作目录。
  ```bash
  pwd
  ```

- **mkdir**：创建新目录。
  ```bash
  mkdir new_directory
  mkdir -p parent_directory/child_directory  # 递归创建目录
  ```

- **rmdir**：删除空目录。
  ```bash
  rmdir empty_directory
  ```

- **rm**：删除文件或目录。
  ```bash
  rm file.txt  # 删除文件
  rm -r directory  # 递归删除目录及其内容
  ```

- **cp**：复制文件或目录。
  ```bash
  cp source_file destination_file  # 复制文件
  cp -r source_directory destination_directory  # 递归复制目录
  ```

- **mv**：移动或重命名文件或目录。
  ```bash
  mv old_name new_name  # 重命名文件或目录
  mv file.txt /new_directory/  # 移动文件到新目录
  ```

- **touch**：创建空文件或更新文件的时间戳。
  ```bash
  touch new_file.txt
  ```

- **cat**：连接文件并打印到标准输出。
  ```bash
  cat file.txt  # 显示文件内容
  ```

- **more**：分页显示文件内容。
  ```bash
  more file.txt
  ```

- **less**：类似more，但更强大。
  ```bash
  less file.txt
  ```

- **head**：显示文件的前几行。
  ```bash
  head -n 10 file.txt  # 显示文件的前10行
  ```

- **tail**：显示文件的后几行。
  ```bash
  tail -n 10 file.txt  # 显示文件的后10行
  ```

**2. 文件权限管理**

- **chmod**：改变文件或目录的权限。
  ```bash
  chmod 755 file.txt  # 设置文件权限为rwxr-xr-x
  chmod u+x file.txt  # 给文件所有者添加执行权限
  ```

- **chown**：改变文件或目录的所有者。
  ```bash
  chown user:group file.txt  # 改变文件的所有者和所属组
  ```

- **chgrp**：改变文件或目录的所属组。
  ```bash
  chgrp group file.txt  # 改变文件的所属组
  ```

**3. 系统管理**

- **ps**：显示当前进程的状态。
  ```bash
  ps -ef  # 显示所有进程
  ```

- **top**：实时显示系统中各个进程的资源使用情况。
  ```bash
  top
  ```

- **kill**：终止进程。
  ```bash
  kill -9 PID  # 强制终止进程
  ```

- **df**：显示文件系统的磁盘空间使用情况。
  ```bash
  df -h  # 以人类可读的格式显示
  ```

- **du**：显示目录或文件的磁盘使用情况。
  ```bash
  du -sh directory  # 显示目录的总大小
  ```

- **free**：显示系统的内存使用情况。
  ```bash
  free -h  # 以人类可读的格式显示
  ```

- **ifconfig**：显示或配置网络接口。
  ```bash
  ifconfig  # 显示网络接口信息
  ```

- **ping**：测试网络连通性。
  ```bash
  ping www.example.com  # 测试与www.example.com的连通性
  ```

- **netstat**：显示网络连接、路由表、接口状态等。
  ```bash
  netstat -an  # 显示所有网络连接
  ```

- **shutdown**：关闭或重启系统。
  ```bash
  shutdown -h now  # 立即关机
  shutdown -r now  # 立即重启
  ```

- **reboot**：重启系统。
  ```bash
  reboot
  ```

#### 三、Linux的高级操作

**1. 软件包管理**

- **apt-get**（适用于Debian系，如Ubuntu）
  ```bash
  sudo apt-get update  # 更新软件包列表
  sudo apt-get upgrade  # 升级所有已安装的软件包
  sudo apt-get install package_name  # 安装软件包
  sudo apt-get remove package_name  # 删除软件包
  sudo apt-get autoremove  # 删除不再需要的包
  ```

- **yum**（适用于Red Hat系，如CentOS）
  ```bash
  sudo yum update  # 更新所有包
  sudo yum install package_name  # 安装软件包
  sudo yum remove package_name  # 删除软件包
  sudo yum clean all  # 清理缓存
  ```

**2. 用户和组管理**

- **useradd**：添加新用户。
  ```bash
  sudo useradd -m new_user  # 创建新用户并创建主目录
  sudo passwd new_user  # 设置新用户的密码
  ```

- **usermod**：修改用户信息。
  ```bash
  sudo usermod -aG group_name user_name  # 将用户添加到组
  ```

- **userdel**：删除用户。
  ```bash
  sudo userdel -r user_name  # 删除用户及其主目录
  ```

- **groupadd**：添加新组。
  ```bash
  sudo groupadd new_group
  ```

- **groupdel**：删除组。
  ```bash
  sudo groupdel group_name
  ```

**3. Shell脚本**

Shell脚本是Linux系统管理和自动化任务的重要工具。以下是一个简单的Shell脚本示例：

```bash
#!/bin/bash

# 打印当前日期和时间
echo "Current date and time: $(date)"

# 创建一个目录
mkdir -p /tmp/my_directory

# 进入目录
cd /tmp/my_directory

# 创建一个文件
touch my_file.txt

# 写入内容到文件
echo "Hello, World!" > my_file.txt

# 显示文件内容
cat my_file.txt
```

保存上述内容为`script.sh`，然后通过以下命令执行：

```bash
chmod +x script.sh  # 赋予执行权限
./script.sh  # 执行脚本
```

#### 四、Linux的网络配置

**1. 配置静态IP地址**

编辑网络配置文件（例如在CentOS上）：

```bash
sudo vi /etc/sysconfig/network-scripts/ifcfg-eth0
```

添加或修改以下内容：

```bash
BOOTPROTO=static
ONBOOT=yes
IPADDR=192.168.1.100
NETMASK=255.255.255.0
GATEWAY=192.168.1.1
DNS1=8.8.8.8
DNS2=8.8.4.4
```

重启网络服务：

```bash
sudo systemctl restart network

```

**2. 配置DNS**

编辑`/etc/resolv.conf`文件：

```bash
sudo vi /etc/resolv.conf
```

添加以下内容：

```bash
nameserver 8.8.8.8
nameserver 8.8.4.4
```

**3. 防火墙管理**

在CentOS上使用`firewalld`：

```bash
sudo systemctl start firewalld  # 启动防火墙
sudo systemctl enable firewalld  # 开机启动防火墙
sudo firewall-cmd --list-all  # 查看防火墙规则
sudo firewall-cmd --add-port=80/tcp --permanent  # 添加规则
sudo firewall-cmd --reload  # 重载防火墙规则
```

#### 五、Linux的日志管理

Linux系统日志通常保存在`/var/log`目录下。常见的日志文件包括：

- **/var/log/messages**：系统消息。
- **/var/log/syslog**：系统日志。
- **/var/log/dmesg**：内核消息。
- **/var/log/boot.log**：启动日志。

查看日志内容：

```bash
cat /var/log/messages
```

使用`grep`搜索特定内容：

```bash
grep "error" /var/log/messages
```

#### 六、Linux的性能监控

**1. top**

实时显示系统中各个进程的资源使用情况。

```bash
top
```

**2. vmstat**

报告虚拟内存、进程、I/O等信息。

```bash
vmstat 1  # 每秒更新一次
```

**3. iostat**

监控系统输入/输出设备。

```bash
iostat 1  # 每秒更新一次
```

**4. mpstat**

监控CPU统计信息。

```bash
mpstat -P ALL 1  # 监控所有CPU，每秒更新一次
```

**5. netstat**

监控网络连接和流量。

```bash
netstat -an
```

#### 七、Linux的安全性

**1. SELinux**

SELinux（Security-Enhanced Linux）是一个强制访问控制系统，提供了更细粒度的安全控制。

查看SELinux状态：

```bash
sestatus
```

**2. AppArmor**

AppArmor是另一种Linux安全模块，提供了基于路径的访问控制。

**3. 权限管理**

合理设置文件和目录的权限，避免使用root用户进行日常操作。

**4. 防火墙**

配置iptables或firewalld防火墙规则，限制不必要的网络访问。

**5. 定期更新**

定期更新系统和软件包，修复安全漏洞。

#### 八、Linux的备份与恢复

**1. tar**

打包和压缩文件。

```bash
tar -czvf archive_name.tar.gz /path/to/directory
```

**2. rsync**

同步文件和目录。

```bash
rsync -avz /source/directory user@remote_host:/destination/directory
```

**3. dump**

备份文件系统。

```bash
dump -0 /path/to/directory
```

**4. restore**

恢复文件系统。

```bash
restore -rf /dev/fd0
```

#### 九、Linux的故障排除

**1. 检查磁盘空间**

```bash
df -h
```

**2. 检查磁盘健康**

使用`smartctl`检查磁盘SMART状态。

```bash
smartctl -a /dev/sda
```

**3. 检查日志文件**

查看`/var/log`目录下的日志文件，查找错误信息。

**4. 网络诊断**

使用`ping`、`traceroute`等工具诊断网络问题。

```bash
ping www.example.com
traceroute www.example.com
```

**5. 系统监控**

使用`top`、`vmstat`等工具监控系统性能。

#### 十、Linux的编程开发

**1. gcc/g++**

编译C/C++程序。

```bash
gcc -o program program.c
g++ -o program program.cpp
```

**2. make**

自动化编译和链接。

```bash
make -f Makefile
```

**3. gdb**

调试C/C++程序。

```bash
gdb program
```

**4. vim/emacs**

强大的文本编辑器。

**5. git**

版本控制。

```bash
git clone https://github.com/user/repo.git
git add .
git commit -m "message"
git push origin master
```

**6. Python**

Python编程。

```bash
python3 script.py
```

**7. Perl**

Perl编程。

```bash
perl script.pl
```

#### 十一、Linux的容器技术

**1. Docker**

Docker是一个开源的容器化平台，允许开发者打包应用以及应用的依赖包到一个可移植的容器中，然后发布到任何流行的Linux机器上，也可以实现虚拟化。

拉取和运行Docker镜像：

```bash
docker pull ubuntu
docker run -it ubuntu /bin/bash
```

管理Docker容器：

```bash
docker ps  # 查看运行中的容器
docker stop container_id  # 停止容器
docker rm container_id  # 删除容器
```

**2. Kubernetes**

Kubernetes是一个开源的容器编排系统，用于自动化部署、扩展和管理容器化应用程序。

```bash
kubectl run my-pod --image=ubuntu --command -- /bin/bash
```

#### 十二、Linux的虚拟化技术

**1. KVM**

KVM（Kernel-based Virtual Machine）是一个基于Linux内核的虚拟化技术。

**2. Xen**

Xen是一个开源的虚拟化平台，支持多种操作系统。

**3. VirtualBox**

VirtualBox是一个开源的虚拟化软件，可以在多种操作系统上运行。


