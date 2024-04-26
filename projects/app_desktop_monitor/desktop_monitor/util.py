import requests


def get_pc_info(site_addr):
    url = site_addr + '/'
    try:
        res = requests.post(url)
        if res.status_code != 200:
            print("-- [Error] status code:", res.status_code)
            return None
        info = res.json()
        return info
    except Exception as e:
        print("-- [Error]", e)
        return None
