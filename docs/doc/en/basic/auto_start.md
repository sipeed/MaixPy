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

For MaixCAM, since the underlying system is Linux, if you are familiar with Linux, you can edit the startup scripts in `/etc/rc.local` or `/etc/init.d`.

However, it is important to note that this method may cause the application to continue running when MaixVision connects, thereby occupying resources (such as the screen and camera) which might prevent MaixVision from running programs normally. The first two methods allow MaixVision to terminate the program upon connection to run its own programs.

Thus, this method is more suitable for running background processes that do not occupy screen and camera resources. Generally, if you are not familiar with Linux, it is not recommended to use this method.

