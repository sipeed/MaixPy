'''
    Usage: python gen_app_info.py apps_dir
'''
import os
import yaml
import sys

app_info_content = '''
[basic]
version=1

'''

if len(sys.argv) > 1:
    apps_dir = sys.argv[1]
else:
    apps_dir = os.path.abspath(os.path.dirname(__file__))

app_info_path = os.path.join(apps_dir, "app.info")

high_priority_apps = [
    "app_store",
    "settings"
]

apps_info = {}
for name in os.listdir(apps_dir):
    app_info_str = ""
    app_dir = os.path.join(apps_dir, name)
    if not os.path.isdir(app_dir):
        continue
    app_yaml_path = os.path.join(app_dir, "app.yaml")
    with open(app_yaml_path, "r") as f:
        app_info = yaml.safe_load(f)
    if app_info["id"] == "launcher":
        continue
    app_info_str += f'[{app_info["id"]}]\n'
    valid_keys = ["name", "version", "icon", "author", "desc"]
    for k, v in app_info.items():
        valid = False
        for valid_k in valid_keys:
            if k.startswith(valid_k):
                valid = True
                break
        if not valid:
            continue
        app_info_str += f'{k}={v}\n'
    if "main.py" in os.listdir(app_dir):
        exec_path = "main.py"
    else:
        exec_path = app_info["id"]
    app_info_str += f"exec={exec_path}\n"
    app_info_str += "\n"
    apps_info[app_info["id"]] = app_info_str

for id in high_priority_apps:
    if id in apps_info:
        app_info_content += apps_info[id]

li = []
for id, content in apps_info.items():
    if id in high_priority_apps:
        continue
    li.append((id, content))
li = sorted(li, key=lambda x:x[0])
for id, content in li:
    app_info_content += content

with open(app_info_path, "w", encoding="utf-8") as f:
    f.write(app_info_content)
