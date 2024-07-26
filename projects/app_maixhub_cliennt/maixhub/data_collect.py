import requests
from .trans import tr

def upload_heartbeat(url, token):
    '''
        send heartbeat to server, so server can know us
        @return (success, msg)
    '''
    headers = {
        "token": token,
        "type": "heartbeat"
    }
    try:
        res = requests.post(url, headers = headers)
        if res.status_code != 200:
            if res.status_code == 401: # 鉴权失败，提示重新扫码
                return (False, tr("Auth failed, re-scan QR code"))
            return False, "Server refused"
    except Exception as e:
        e = str(e)
        if "Connection refused" in e:
            return False, "Connection refused"
        return False, "Network error"
    return True, ""

def upload_dataset(img, url, token, format = "jpeg"):
    '''
        @img path to image or bytes
        @return (success, msg)
    '''
    if type(img) == str:
        from PIL import Image
        from io import BytesIO

        jpeg = BytesIO()
        img = Image.open(img)
        img.save(jpeg, format="JPEG")
        img_bytes = jpeg.getvalue()
    elif type(img) == bytes:
        img_bytes = img
    else:
        raise Exception("img must be a path or bytes")

    headers = {
        "token": token,
        "format": format,
        "type": "file"
    }
    try:
        res = requests.post(url, data = img_bytes, headers = headers)
        if res.status_code != 200:
            if res.status_code == 401: # 鉴权失败，提示重新扫码
                return (False, tr("Auth failed, re-scan QR code"))
            return False, "Server refused"
    except Exception as e:
        e = str(e)
        if "Connection refused" in e:
            return False, "Connection refused"
        return False, "Network error"
    return True, ""

if __name__ == "__main__":
    import flask
    from io import BytesIO
    from PIL import Image
    import threading, time
    import sys

    download_model_url = sys.argv[1] # 一个可以下载模型的 url， 从 maixhub 的部署页面拿到，注意连接有有效期限的

    app = flask.Flask(__name__)
    @app.route("/upload", methods=["POST"])
    def upload():
        img_bytes = flask.request.data
        format = flask.request.headers["format"]
        token = flask.request.headers["token"]
        print("token:", token)
        print("format:", format)
        jpeg = BytesIO(img_bytes)
        img = Image.open(jpeg)
        img.show()
        return "ok"

    @app.route("/deploy", methods=["POST"])
    def deploy():
        token = flask.request.headers.get("token", "")
        return {
            "id": "123",
            "model": download_model_url,
            "platform": "awnn",
            "board": "m2-v831-dock",
            "name": "卡片1",
            "label_type": "classification",
            "data_type": "image"
        }

    def upload_thread(img, url, token):
        time.sleep(1)
        success, msg = upload_dataset(img, url, token)
        print("upload result:", success, msg)

    t = threading.Thread(target=upload_thread, args=("./assets/test.jpg", "http://localhost:5000/upload", "1234567890"))
    t.setDaemon(True)
    t.start()

    app.run(host="0.0.0.0", port=5000)

    t.join()
