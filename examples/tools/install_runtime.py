import os

def install_runtime():
    cmd = f"/maixapp/apps/app_store/settings install_runtime"
    err_code = os.system(cmd)
    if err_code != 0:
        print("[ERROR] Install failed, error code:", err_code)
    else:
        print(f"Install runtime success")

install_runtime()
