---
title: MaixPy/MaixCAM Application Auto-Start at Boot
---

Packaged applications can be set to automatically start when the device boots up, bypassing the application menu and directly launching the specified application.

## Method One for Setting Application Auto-Start

First, package and install the application, then go to `Settings -> Auto-Start` on your device to select the application you want to auto-start. To cancel auto-start, you can also adjust it here.

## Method Two for Setting Application Auto-Start

Run the Python script to set up, and modify the `new_autostart_app_id` variable in the script to the `app_id` you want to set. All installed `app_id`s will be printed out when you run the script, so you can run it once to find the desired `app_id`, modify the variable, and then run it again. To cancel the autostart setting, set it to `None`.

This script can also be found in the `MaixPy` examples under `examples/tools` as `set_autostart.py`:

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

## Method Three for Setting Application Auto-Start

You can also modify the `/maixapp/auto_start.txt` file in your device to set it up. For methods on file transfer, refer to the previous documentation.
* First, determine the `id` of the application you want to set. This is set when you package the application; if it's not an application you packaged yourself, you can install it on the device and check the folder names under the device's `/maixapp/apps/` directory, which are the application names (or you can download and check the device's `/maixapp/apps/app.info` file, where the application `id` is indicated inside the `[]` brackets).
* Then write the `id` into the `/maixapp/auto_start.txt` file. (You can create the file locally on your computer, and then transfer it to the device using `MaixVision`.)
* To cancel, delete the `/maixapp/auto_start.txt` file on the device.

## Other Methods


Since MaixCAM runs on a Linux-based system, if you're familiar with Linux, you can also configure system startup by directly editing startup scripts:

* For **MaixCAM/MaixCAM-Pro**, edit `/etc/rc.local` or startup scripts under `/etc/init.d`.
* For **MaixCAM2**, which uses **systemd** for startup management, add a service file under `/etc/systemd/system`, then enable it with `systemctl enable xxxx.service`. You can refer to `launcher.service`, which is the default launcher program.

> ⚠️ However, note that this approach **prevents MaixVision from stopping the running application during connection**, which may cause **resource conflicts** (e.g., screen or camera already in use), and **MaixVision might fail to run programs** properly.

In contrast, the first two application auto-start methods allow MaixVision to **gracefully stop the running app** when connecting to the device.

Therefore, this method is **more suitable for background processes** that don’t require access to the screen or camera. If you're not familiar with Linux, this approach is **not recommended**, as it can easily lead to resource conflicts involving the screen or camera.
