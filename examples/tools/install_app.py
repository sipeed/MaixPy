import os

def install_app(pkg_path):
    if not os.path.exists(pkg_path):
        raise Exception(f"package {pkg_path} not found")
    cmd = f"/usr/bin/app_store_cli install {pkg_path}"
    err_code = os.system(cmd)
    if err_code != 0:
        print("[ERROR] Install failed, error code:", err_code)
    else:
        print(f"Install {pkg_path} success")

pkg_path = "/root/my_app_v1.0.0.zip"

install_app(pkg_path)
