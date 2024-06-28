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


