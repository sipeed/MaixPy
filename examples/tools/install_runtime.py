import os

def install_runtime():
    cmd = f"chmod +x /maixapp/apps/settings/settings && /maixapp/apps/settings/settings install_runtime"
    err_code = os.system(cmd)
    if err_code != 0:
        print("[ERROR] Install failed, error code:", err_code)
    else:
        print(f"Install runtime success")

install_runtime()
