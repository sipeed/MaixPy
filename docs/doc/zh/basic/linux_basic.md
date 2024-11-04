---
title: Linux 基础知识
update:
  - date: 2024-03-19
    author: neucrack
    version: 1.0.0
    content: 填加文档
  - date: 2024-10-26
    author: YWJ
    version: 2.0.0
    content: 增加常用命令文档
---

## 简介

本章内容对于刚入门的同学来说，可以先跳过此章节，在学会 MaixPy 基础开发后再来学习也是可以的。

最新的 MaixPy 支持的 MaixCAM 硬件支持跑 Linux 系统，所以 MaixPy 底层都是基于 Linux 系统进行开发的。
虽然 Sipeed 开发的 MaixPy 已经为开发者们做了很多工作，即使不知道 Linux 系统知识也能愉快使用，但是以防在某些情况下需要一些底层操作，以及方便未接触过 Linux 的开发者学习，这里写一些 Linux 基础知识。


## 为什么需要 Linux 系统

Linux 的介绍请大家自行查阅了解，这里用通俗的看起来不太专业的话语简单举几个例子方便初学者理解：
* 在单片机中，我们的程序是一个死循环程序，用上 Linux 后我们可以同时跑很多程序，每个程序看起来都独立在同时运行，每个程序具体怎么执行的由操作系统实现。
* 基于 Linux 的开发者众多，需要功能和驱动可以很方便地找到，不需要自己再实现一遍。
* 基于 Linux 配套的软件工具丰富，可以很方便地进行开发和调试，比如在本教程没有提到的一些 Linux 通用工具理论上也是可以使用的。


## Linux 系统大家族

Linux 是一个开源操作系统内核，提供了操作系统基本的内容，使用其本身并不能像 Windows 一样普通用户能开箱即用，所以开源社区基于 Linux 内核发展出了很多版本（发行版），比如 `Ubuntu` 应该是用户量最大的发行版，使用人数较多，资料多，入门建议选择，其它的还有 `Arch` `CentOS` 等等非常多，全部都是基于 Linux 内核，所以大家日常都称为 Linux。
这众多系统的不同就是 界面、用户交互体验、驱动、预装软件、软件管理器（包管理器）等等，新手可以选择`Ubuntu`再探索其它系统。

对于 MaixCAM，理论上也可以安装`Ubuntu`等系统，不过由于 MaixCAM 的内存只有 256MB，比较有限，而且 ubuntu 有很多臃肿的软件实际部署用不到， MaixCAM 使用了基于`Linux`内核+`buildroot`文件系统构建的系统，代码开源在[github.com/sipeed/LicheeRV-Nano-Build](https://github.com/sipeed/LicheeRV-Nano-Build)。有兴趣的可以搜索相关词汇了解。


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

## MaixCAM 执行 shell 终端命令

对于 `MaixCAM` 有几种方法可以和其系统`shell`进行交互：
* 在电脑终端通过`ssh root@192.168.0.123` 来连接 `MaixCAM`，默认密码是`root`。
* 通过 `MaixVision` 的`终端`功能来连接（MaixVision 版本 >= 1.2.0）。
* 通过 Python 脚本来执行，最简单的就是使用`os.system()`函数，比如
```python
import os
os.system("echo hello")
```
另外`Python`还有其它模块可以执行 shell 命令，比如`subprocess` 模块：
```python
import subprocess

# 要执行的命令
command = ["echo", "Hello, World!"]

# 使用 Popen 执行命令
process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# 获取输出和错误
stdout, stderr = process.communicate()

# 打印输出
print("标准输出:", stdout.decode())
print("标准错误:", stderr.decode())
```


## Linux 常用命令参考

这里列一些常见的 Linux 命令操作，方便查阅。

注意以下为社区成员贡献文档，只做参考，以及并不是所有命令是适用于 MaixCAM 的系统。

### 文件和目录操作

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

### 文件权限管理

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

### 系统管理

- **ps**：显示当前进程的状态。
  ```bash
  ps -ef  # 显示所有进程
  ```

- **top**：实时显示系统中各个进程的资源使用情况。
  ```bash
  top
  ```
  ```bash
  htop
  ```

- **kill**：终止进程。
  ```bash
  kill -2 PID  # 向进程发送 Ctrl+C 信号
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
  shutdown         # 立即关机
  shutdown -h now  # 立即关机
  shutdown -r now  # 立即重启
  ```

- **reboot**：重启系统。
  ```bash
  reboot
  ```

### 软件包管理

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

### 用户和组管理

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

### Shell脚本

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

### Linux 的网络配置

#### 配置静态IP地址

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

#### 配置 DNS

编辑`/etc/resolv.conf`文件：

```bash
sudo vi /etc/resolv.conf
```

添加以下内容：

```bash
nameserver 8.8.8.8
nameserver 8.8.4.4
```

#### 防火墙管理

在CentOS上使用`firewalld`：

```bash
sudo systemctl start firewalld  # 启动防火墙
sudo systemctl enable firewalld  # 开机启动防火墙
sudo firewall-cmd --list-all  # 查看防火墙规则
sudo firewall-cmd --add-port=80/tcp --permanent  # 添加规则
sudo firewall-cmd --reload  # 重载防火墙规则
```

### Linux 的日志管理

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

### Linux的性能监控

#### top

实时显示系统中各个进程的资源使用情况。

```bash
top
```
或者
```bash
htop
```

#### vmstat

报告虚拟内存、进程、I/O等信息。

```bash
vmstat 1  # 每秒更新一次
```

####iostat

监控系统输入/输出设备。

```bash
iostat 1  # 每秒更新一次
```

#### mpstat

监控CPU统计信息。

```bash
mpstat -P ALL 1  # 监控所有CPU，每秒更新一次
```

#### netstat

监控网络连接和流量。

```bash
netstat -an
```

### Linux 的安全性

#### SELinux

SELinux（Security-Enhanced Linux）是一个强制访问控制系统，提供了更细粒度的安全控制。

查看SELinux状态：

```bash
sestatus
```

#### AppArmor

AppArmor是另一种Linux安全模块，提供了基于路径的访问控制。

#### 权限管理

合理设置文件和目录的权限，避免使用root用户进行日常操作。

#### 防火墙

配置iptables或firewalld防火墙规则，限制不必要的网络访问。

#### 定期更新

定期更新系统和软件包，修复安全漏洞。

### Linux 的备份与恢复

#### tar

打包和压缩文件。

```bash
tar -czvf archive_name.tar.gz /path/to/directory
```

#### rsync

同步文件和目录。

```bash
rsync -avz /source/directory user@remote_host:/destination/directory
```

#### dump
备份文件系统。

```bash
dump -0 /path/to/directory
```

#### restore

恢复文件系统。

```bash
restore -rf /dev/fd0
```

### Linux 的故障排除

#### 检查磁盘空间

```bash
df -h
```

#### 检查磁盘健康

使用`smartctl`检查磁盘SMART状态。

```bash
smartctl -a /dev/sda
```

#### 检查日志文件

查看`/var/log`目录下的日志文件，查找错误信息。

#### 网络诊断

使用`ping`、`traceroute`等工具诊断网络问题。

```bash
ping www.example.com
traceroute www.example.com
```

#### 系统监控

使用`top`、`vmstat`等工具监控系统性能。

### Linux的编程开发

#### gcc/g++

编译C/C++程序。

```bash
gcc -o program program.c
g++ -o program program.cpp
```

#### make

自动化编译和链接。

```bash
make -f Makefile
```

#### gdb

调试C/C++程序。

```bash
gdb program
```

#### vim/emacs

强大的文本编辑器。

#### git

版本控制。

```bash
git clone https://github.com/user/repo.git
git add .
git commit -m "message"
git push origin master
```

#### Python

Python编程。

```bash
python3 script.py
```

#### Perl

Perl编程。

```bash
perl script.pl
```

### Linux 的容器技术

#### Docker

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

#### Kubernetes

Kubernetes是一个开源的容器编排系统，用于自动化部署、扩展和管理容器化应用程序。

```bash
kubectl run my-pod --image=ubuntu --command -- /bin/bash
```

### Linux 的虚拟化技术

#### KVM

KVM（Kernel-based Virtual Machine）是一个基于Linux内核的虚拟化技术。

#### Xen

Xen是一个开源的虚拟化平台，支持多种操作系统。

#### VirtualBox

VirtualBox是一个开源的虚拟化软件，可以在多种操作系统上运行。






