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

## The Linux System Family

Linux is an open-source operating system kernel that provides the basic content of an operating system. Using it on its own cannot be used out-of-the-box by ordinary users like Windows, so the open-source community has developed many versions (distributions) based on the Linux kernel. For example, `Ubuntu` is probably the distribution with the largest user base, with many users, abundant resources, and is recommended for beginners. There are also many others such as `Arch` and `CentOS`. They are all based on the Linux kernel, so they are commonly referred to as Linux in daily use.
The differences among these many systems lie in the user interface, user interaction experience, drivers, pre-installed software, software managers (package managers), and so on. Beginners can start with `Ubuntu` and then explore other systems.

For MaixCAM, it is theoretically possible to install systems such as `Ubuntu`. However, since MaixCAM has only 256MB of memory, which is quite limited, and Ubuntu comes with many bloated software packages that are not needed in actual deployment, MaixCAM uses a system built with the `Linux` kernel + the `buildroot` file system. The source code is open-sourced at [github.com/sipeed/LicheeRV-Nano-Build](https://github.com/sipeed/LicheeRV-Nano-Build). Those who are interested can search for related terms to learn more.

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

For example, we can enter `ssh root@maixcam-xxxx.local` in the Terminal tool on a Windows system with PowerShell or on a Linux system. You can find the specific name in the device's `Settings->Device Information`, which allows us to connect to the device through the terminal (the username and password of MaixCam and MaixCam Pro are both `root`; for MaixCam2, the username is `root` and the password is `sipeed`).

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

## Run shell commands on MaixCAM

For `MaixCAM`, there are several ways to interact with the system `shell`:
* Connect to `MaixCAM` from the computer terminal via `ssh root@192.168.0.123`, the default password is `root`.
* Connect through the `Terminal` feature of `MaixVision` (MaixVision version >= 1.2.0).
* Execute commands via a Python script. The simplest way is to use the `os.system()` function, for example:
```python
import os
os.system("echo hello")
```
`Python` also has other modules for executing shell commands, such as the `subprocess` module:
```python
import subprocess

# command to execute
command = ["echo", "Hello, World!"]

# execute the command with Popen
process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# get the output and errors
stdout, stderr = process.communicate()

# print the output
print("stdout:", stdout.decode())
print("stderr:", stderr.decode())
```

> Note: For MaixCam, the username and password to enter the shell terminal are both `root`; for MaixCam2, the username is `root` and the password is `sipeed`.

## Common Linux Command Reference

This section lists some common Linux command operations for quick reference.

Note that the following is a community-contributed document and is for reference only, and not all commands are applicable to the MaixCAM system.

### File and Directory Operations

- **ls**: List directory contents.
  ```bash
  ls -l  # Long listing
  ls -a  # Show hidden files
  ```

- **cd**: Change the current directory.
  ```bash
  cd /home/user  # Enter the /home/user directory
  cd ..  # Go back to the parent directory
  cd ~  # Go back to the user's home directory
  ```

- **pwd**: Print the current working directory.
  ```bash
  pwd
  ```

- **mkdir**: Create a new directory.
  ```bash
  mkdir new_directory
  mkdir -p parent_directory/child_directory  # Create directories recursively
  ```

- **rmdir**: Remove an empty directory.
  ```bash
  rmdir empty_directory
  ```

- **rm**: Remove files or directories.
  ```bash
  rm file.txt  # Remove a file
  rm -r directory  # Recursively remove a directory and its contents
  ```

- **cp**: Copy files or directories.
  ```bash
  cp source_file destination_file  # Copy a file
  cp -r source_directory destination_directory  # Recursively copy a directory
  ```

- **mv**: Move or rename files or directories.
  ```bash
  mv old_name new_name  # Rename a file or directory
  mv file.txt /new_directory/  # Move a file to a new directory
  ```

- **touch**: Create an empty file or update the file's timestamp.
  ```bash
  touch new_file.txt
  ```

- **cat**: Concatenate files and print to standard output.
  ```bash
  cat file.txt  # Display the file contents
  ```

- **more**: Display file contents page by page.
  ```bash
  more file.txt
  ```

- **less**: Similar to more, but more powerful.
  ```bash
  less file.txt
  ```

- **head**: Display the first few lines of a file.
  ```bash
  head -n 10 file.txt  # Display the first 10 lines of the file
  ```

- **tail**: Display the last few lines of a file.
  ```bash
  tail -n 10 file.txt  # Display the last 10 lines of the file
  ```

### File Permission Management

- **chmod**: Change the permissions of a file or directory.
  ```bash
  chmod 755 file.txt  # Set file permissions to rwxr-xr-x
  chmod u+x file.txt  # Add execute permission for the file owner
  ```

- **chown**: Change the owner of a file or directory.
  ```bash
  chown user:group file.txt  # Change the file's owner and group
  ```

- **chgrp**: Change the group of a file or directory.
  ```bash
  chgrp group file.txt  # Change the file's group
  ```

### System Management

- **ps**: Show the status of current processes.
  ```bash
  ps -ef  # Show all processes
  ```

- **top**: Display resource usage of processes in real time.
  ```bash
  top
  ```
  ```bash
  htop
  ```

- **kill**: Terminate a process.
  ```bash
  kill -2 PID  # Send a Ctrl+C signal to the process
  kill -9 PID  # Force kill the process
  ```

- **df**: Display disk space usage of file systems.
  ```bash
  df -h  # Display in human-readable format
  ```

- **du**: Display disk usage of a directory or file.
  ```bash
  du -sh directory  # Show the total size of a directory
  ```

- **free**: Display the system's memory usage.
  ```bash
  free -h  # Display in human-readable format
  ```

- **ifconfig**: Display or configure network interfaces.
  ```bash
  ifconfig  # Display network interface information
  ```

- **ping**: Test network connectivity.
  ```bash
  ping www.example.com  # Test connectivity to www.example.com
  ```

- **netstat**: Display network connections, routing tables, interface stats, etc.
  ```bash
  netstat -an  # Display all network connections
  ```

- **shutdown**: Shut down or reboot the system.
  ```bash
  shutdown         # Shut down immediately
  shutdown -h now  # Shut down immediately
  shutdown -r now  # Reboot immediately
  ```

- **reboot**: Reboot the system.
  ```bash
  reboot
  ```

### Package Management

- **apt-get** (for Debian-based systems, such as Ubuntu)
  ```bash
  sudo apt-get update  # Update the package list
  sudo apt-get upgrade  # Upgrade all installed packages
  sudo apt-get install package_name  # Install a package
  sudo apt-get remove package_name  # Remove a package
  sudo apt-get autoremove  # Remove packages no longer needed
  ```

- **yum** (for Red Hat-based systems, such as CentOS)
  ```bash
  sudo yum update  # Update all packages
  sudo yum install package_name  # Install a package
  sudo yum remove package_name  # Remove a package
  sudo yum clean all  # Clean the cache
  ```

### User and Group Management

- **useradd**: Add a new user.
  ```bash
  sudo useradd -m new_user  # Create a new user and create a home directory
  sudo passwd new_user  # Set the password for the new user
  ```

- **usermod**: Modify user information.
  ```bash
  sudo usermod -aG group_name user_name  # Add the user to a group
  ```

- **userdel**: Delete a user.
  ```bash
  sudo userdel -r user_name  # Delete the user and its home directory
  ```

- **groupadd**: Add a new group.
  ```bash
  sudo groupadd new_group
  ```

- **groupdel**: Delete a group.
  ```bash
  sudo groupdel group_name
  ```

### Shell Scripts

Shell scripts are an important tool for Linux system administration and task automation. Here is a simple shell script example:

```bash
#!/bin/bash

# Print the current date and time
echo "Current date and time: $(date)"

# Create a directory
mkdir -p /tmp/my_directory

# Enter the directory
cd /tmp/my_directory

# Create a file
touch my_file.txt

# Write content to the file
echo "Hello, World!" > my_file.txt

# Display the file contents
cat my_file.txt
```

Save the above content as `script.sh`, then execute it with the following commands:

```bash
chmod +x script.sh  # Grant execute permission
./script.sh  # Execute the script
```

### Linux Network Configuration

#### Configure a static IP address

Edit the network configuration file (for example, on CentOS):

```bash
sudo vi /etc/sysconfig/network-scripts/ifcfg-eth0
```

Add or modify the following content:

```bash
BOOTPROTO=static
ONBOOT=yes
IPADDR=192.168.1.100
NETMASK=255.255.255.0
GATEWAY=192.168.1.1
DNS1=8.8.8.8
DNS2=8.8.4.4
```

Restart the network service:

```bash
sudo systemctl restart network

```

#### Configure DNS

Edit the `/etc/resolv.conf` file:

```bash
sudo vi /etc/resolv.conf
```

Add the following content:

```bash
nameserver 8.8.8.8
nameserver 8.8.4.4
```

#### Firewall management

Use `firewalld` on CentOS:

```bash
sudo systemctl start firewalld  # Start the firewall
sudo systemctl enable firewalld  # Enable the firewall on boot
sudo firewall-cmd --list-all  # View firewall rules
sudo firewall-cmd --add-port=80/tcp --permanent  # Add a rule
sudo firewall-cmd --reload  # Reload firewall rules
```

### Linux Log Management

Linux system logs are usually stored in the `/var/log` directory. Common log files include:

- **/var/log/messages**: System messages.
- **/var/log/syslog**: System logs.
- **/var/log/dmesg**: Kernel messages.
- **/var/log/boot.log**: Boot logs.

View log contents:

```bash
cat /var/log/messages
```

Use `grep` to search for specific content:

```bash
grep "error" /var/log/messages
```

### Linux Performance Monitoring

#### top

Display resource usage of processes in real time.

```bash
top
```
Or
```bash
htop
```

#### vmstat

Report virtual memory, processes, I/O, and other information.

```bash
vmstat 1  # Update once per second
```

#### iostat

Monitor system input/output devices.

```bash
iostat 1  # Update once per second
```

#### mpstat

Monitor CPU statistics.

```bash
mpstat -P ALL 1  # Monitor all CPUs, update once per second
```

#### netstat

Monitor network connections and traffic.

```bash
netstat -an
```

### Linux Security

#### SELinux

SELinux (Security-Enhanced Linux) is a mandatory access control system that provides finer-grained security control.

View SELinux status:

```bash
sestatus
```

#### AppArmor

AppArmor is another Linux security module that provides path-based access control.

#### Permission Management

Set file and directory permissions reasonably, and avoid using the root user for daily operations.

#### Firewall

Configure iptables or firewalld firewall rules to restrict unnecessary network access.

#### Regular Updates

Regularly update the system and software packages to fix security vulnerabilities.

### Linux Backup and Recovery

#### tar

Archive and compress files.

```bash
tar -czvf archive_name.tar.gz /path/to/directory
```

#### rsync

Synchronize files and directories.

```bash
rsync -avz /source/directory user@remote_host:/destination/directory
```

#### dump

Back up a file system.

```bash
dump -0 /path/to/directory
```

#### restore

Restore a file system.

```bash
restore -rf /dev/fd0
```

### Linux Troubleshooting

#### Check disk space

```bash
df -h
```

#### Check disk health

Use `smartctl` to check the disk's SMART status.

```bash
smartctl -a /dev/sda
```

#### Check log files

View the log files in the `/var/log` directory to find error information.

#### Network diagnostics

Use tools such as `ping`, `traceroute` to diagnose network problems.

```bash
ping www.example.com
traceroute www.example.com
```

#### System monitoring

Use tools such as `top`, `vmstat` to monitor system performance.

### Linux Programming and Development

#### gcc/g++

Compile C/C++ programs.

```bash
gcc -o program program.c
g++ -o program program.cpp
```

#### make

Automate compilation and linking.

```bash
make -f Makefile
```

#### gdb

Debug C/C++ programs.

```bash
gdb program
```

#### vim/emacs

Powerful text editors.

#### git

Version control.

```bash
git clone https://github.com/user/repo.git
git add .
git commit -m "message"
git push origin master
```

#### Python

Python programming.

```bash
python3 script.py
```

#### Perl

Perl programming.

```bash
perl script.pl
```

### Linux Container Technology

#### Docker

Docker is an open-source containerization platform that allows developers to package an application and its dependencies into a portable container, then publish it to any popular Linux machine, and can also implement virtualization.

Pull and run a Docker image:

```bash
docker pull ubuntu
docker run -it ubuntu /bin/bash
```

Manage Docker containers:

```bash
docker ps  # List running containers
docker stop container_id  # Stop a container
docker rm container_id  # Remove a container
```

#### Kubernetes

Kubernetes is an open-source container orchestration system used to automate the deployment, scaling, and management of containerized applications.

```bash
kubectl run my-pod --image=ubuntu --command -- /bin/bash
```

### Linux Virtualization Technology

#### KVM

KVM (Kernel-based Virtual Machine) is a virtualization technology based on the Linux kernel.

#### Xen

Xen is an open-source virtualization platform that supports multiple operating systems.

#### VirtualBox

VirtualBox is an open-source virtualization software that can run on multiple operating systems.

