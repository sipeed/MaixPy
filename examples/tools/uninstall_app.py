import os

def install_app(app_id):
    cmd = f"/usr/bin/app_store_cli uninstall {app_id}"
    err_code = os.system(cmd)
    if err_code != 0:
        print("[ERROR] Uninstall failed, error code:", err_code)
    else:
        print(f"Uninstall {app_id} success")

# you can use list_apps.py to get app_id
app_id = "my_app"
install_app(app_id)

