import configparser

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
