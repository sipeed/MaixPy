import os

def install_maixpy(server):
    cmd = f"pip install maixpy -U -i {server}"
    print("Start install now, wait patiently ...")
    err = os.system(cmd)
    if err != 0:
        print("[ERROR] execute failed, code:", err)
    else:
        print("Install complete")


servers = {
    "pypi": "https://pypi.org/simple",
    "aliyun": "https://mirrors.aliyun.com/pypi/simple",
    "ustc": "https://pypi.mirrors.ustc.edu.cn/simple",
    "163": "https://mirrors.163.com/pypi/simple",
    "douban": "https://pypi.douban.com/simple",
    "tuna": "https://pypi.tuna.tsinghua.edu.cn/simple"
}

# Select server based on your network
server = servers["tuna"]

install_maixpy(server)