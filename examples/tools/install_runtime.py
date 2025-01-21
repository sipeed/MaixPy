import os

def install_runtime(force = False):
    version_path = "/maixapp/maixcam_lib.version"
    if force and os.path.exists(version_path):
        os.remove(version_path)
    cmd = f"chmod +x /maixapp/apps/settings/settings && /maixapp/apps/settings/settings install_runtime"
    err_code = os.system(cmd)
    if err_code != 0:
        print("[ERROR] Install failed, error code:", err_code)
    else:
        print(f"Install runtime success")


force_reinstall = False   # reinstall runtime even we alredy installed.
install_runtime(force_reinstall)
