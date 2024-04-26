from maix import i18n

lang_dict = {
    "zh": {
        "Server": "服务器",
        "scan_qr_title": "扫描二维码以连接",
        "scan_qr_tip1": "1. 确保设备和电脑在同一个局域网内",
        "scan_qr_tip2": "2. 在电脑执行'pip install pc-monitor-server'",
        "scan_qr_tip3": "3. 在电脑执行'pc-monitor-server'启动服务器",
    },
    "en": {
        "scan_qr_title": "Scan QR code to connect",
        "scan_qr_tip1": "1. Make sure device and PC in the same LAN",
        "scan_qr_tip2": "2. Execute 'pip install pc-monitor-server' on PC",
        "scan_qr_tip3": "3. Execute 'pc-monitor-server' on PC",
    }
}

trans = i18n.Trans(lang_dict)
tr = trans.tr

