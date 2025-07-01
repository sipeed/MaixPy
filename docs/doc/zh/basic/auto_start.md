---
title: MaixCAM MaixPy 应用开机自启
---

打包安装好的应用可以设置开机自动启动，这样开机就不会显示应用菜单，直接进入指定的应用。

## 设置应用开机自启方法一

先打包安装好应用，然后在设备`设置 -> 开机自启` 设置中选择需要自动启动的应用即可，取消开机自启也是在这里设置。

## 设置应用开机自启方法二

运行 Python 脚本设置，修改脚本中的`new_autostart_app_id` 变量为你想设置的 `app_id`， 所有已经安装了的`app_id`会在执行脚本时打印出来，可以先执行一遍找到你想设置的`app_id`，修改变量再执行一遍即可，取消自动启动设置为`None`即可。
此脚本也可以在`MaixPy`的`examples/tools`中找到`set_autostart.py`：

```python
import configparser, os

def parse_apps_info():
    info_path = "/maixapp/apps/app.info"
    conf = configparser.ConfigParser()
    conf.read(info_path)
    version = conf["basic"]["version"]
    apps = {}
    for id in list(conf.keys()):
        if id in ["basic", "DEFAULT"]:
            continue
        apps[id] = conf[id]
    return apps

def list_apps():
    apps = parse_apps_info()
    print(f"APP num: {len(apps)}")
    for i, (id, info) in enumerate(apps.items()):
        name_zh = info.get("name[zh]", "")
        print(f"{i + 1}. [{info['name']}] {name_zh}:")
        print(f"    id: {id}")
        print(f"    exec: {info['exec']}")
        print(f"    author: {info['author']}")
        print(f"    desc: {info['desc']}")
        print(f"    desc_zh: {info.get('desc', 'None')}")
        print("")


def get_curr_autostart_app():
    path = "/maixapp/auto_start.txt"
    if os.path.exists(path):
        with open(path, "r") as f:
            app_id = f.readline().strip()
            return app_id
    return None

def set_autostart_app(app_id):
    path = "/maixapp/auto_start.txt"
    if not app_id:
        if os.path.exists(path):
            os.remove(path)
        return
    with open(path, "w") as f:
        f.write(app_id)

if __name__ == "__main__":
    # new_autostart_app_id = "settings"   # change to app_id you want to set
    new_autostart_app_id = None           # remove autostart

    list_apps()
    print("Before set autostart appid:", get_curr_autostart_app())
    set_autostart_app(new_autostart_app_id)
    print("Current autostart appid:", get_curr_autostart_app())

```

## 设置应用开机自启方法三

你也可以通过修改设备中的 `/maixapp/auto_start.txt` 文件来设置，和传输文件的方法请看前面的文档。
* 首先知道你需要设置的应用的 `id` 是什么。在你打包应用的时候设置的；如果不是你自己打包的应用，可以先安装到设备，查看设备`/maixapp/apps/` 目录下的文件夹名就是应用名，（也可以下载查看设备的`/maixapp/apps/app.info` 文件，`[]`中括号部分就是应用`id`）。
* 然后写入 `id` 到 `/maixapp/auto_start.txt` 文件即可。（可以在电脑本地创建文件，然后 `MaixVision` 传输到设备。）
* 如果要取消，删除设备上的 `/maixapp/auto_start.txt` 文件即可。


## 其它方法

因为 MaixCAM 底层是 Linux， 如果你熟悉 Linux，还可以直接编辑系统启动脚本：
* 对于 MaixCAM/MaixCAM-Pro, 编辑`/etc/rc.local` 或者 `/etc/init.d` 下的启动脚本。
* 对于 MaixCAM2，基于 systemd 的启动管理方式，在`/etc/systemd/system`下面添加启动项，然后`systemctl enable xxxx.service`即可使能开机启动，可以参考`launcher.service`即开机起动器程序。

但是需要注意的是，这种方式会让 MaixVision 在连接的时候无法停止这个应用，从而造成资源占用（比如屏幕和摄像头） MaixVision 可能无法正常跑程序，而前两种方法 MaixVision 连接设备时是可以正常让程序退出以供 MaixVsion 跑程序的。

所以这种方法比较适合开机跑一些不会占用屏幕和摄像头等资源的后台进程，一般情况下如果你不熟悉 Linux 不建议这样操作，不然很容易导致屏幕和摄像头资源互相占用出问题。





