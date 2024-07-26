
translations_zh = {
    "func": "功能",
    "ok": "确认",
    "Loading": "加载中",
    "back": "返回",
    "Scan QR code": "扫描二维码",
    "collect": "采集",
    "cancel": "取消",
    "upload": "上传",
    "Upload": "上传",
    "Uploading": "上传中",
    "Upload failed!": "上传失败！",
    "ok back": "确认返回",
    "switch": "切换",
    "save": "保存",
    "Sure to change ?": "确认更改 ？",
    "Collect images": "采集图片",
    "Resolution settings": "分辨率设置",
    "WiFi settings": "WiFi 设置",
    "Exit": "退出",
    "Language settings": "语言设置",
    "connect": "连接",
    "Connect now ?": "现在就连接 ？",
    "Passwd": "密码",
    "Visit": "访问",
    "Connect failed": "连接失败",
    "Connecting": "连接中",
    "Connect timeout": "连接超时",
    "No IP": "无 IP",
    "QR code error": "二维码错误",
    "Connect success": "连接成功",
    "Deploy model": "部署模型",
    "Get model info": "获取模型信息",
    "failed": "失败",
    "Downloading model": "正在下载模型",
    "Download Failed!": "下载失败！",
    "Params error!": "参数错误！",
    "Unzip model": "正在解压模型",
    "Unzip Failed!": "解压失败！",
    "Load model failed": "加载模型失败",
    "Request server error": "请求服务器错误",
    "Loading model": "正在加载模型",
    "Refused": "已拒绝",
    "Canceled": "已取消",
    "view saved": "查看已保存",
    "select": "选择",
    "run": "运行",
    "delete": "删除",
    "Aim to object to detect": "对准物体以开始检测",
    "Response error": "响应错误",
    "collect locally": "本地采集",
    "Can re-enter to change dir": "重进会改变目录",
    "Will save to": "将保存到",
    "Save": "保存",
    "Auth failed, re-scan QR code": "鉴权失败，请重新扫描二维码",
}

curr_language = "en"
curr_trans_dict = {}

def set_language(lang):
    global curr_language, curr_trans_dict
    if lang == "zh":
        curr_language = "zh"
        curr_trans_dict = translations_zh
    else:
        curr_language = "en"
        curr_trans_dict = {}

def tr(msg):
    return curr_trans_dict.get(msg, msg)
