import gc
from maix import display, camera, image, app, time, i18n, touchscreen
from .board import get_board_name, is_support_model_platform
import os
import json
from .data_collect import upload_dataset, upload_heartbeat
from .trans import tr, set_language
from .params import Params
from .utils import download_file, unzip_files, remove_dir, Audio, bytes_to_human
from .demos import load_model_info, load_saved_models, remove_mud_model
from .widgets.list import UI_List

curr_dir = os.path.abspath(os.path.dirname(__file__))
assets_dir = os.path.join(curr_dir, "assets")

paly_key_sound = False
color_green = image.Color.from_rgb(76, 175, 80)

image.load_font("sourcehansans", "/maixapp/share/font/SourceHanSansCN-Regular.otf", size = 28)
image.set_default_font("sourcehansans")
if paly_key_sound:
    audio = Audio(os.path.join(assets_dir, "btn.wav"))

disp = display.Display()
ts = touchscreen.TouchScreen()

def is_in_button(x, y, btn_pos):
    return x > btn_pos[0] and x < btn_pos[0] + btn_pos[2] and y > btn_pos[1] and y < btn_pos[1] + btn_pos[3]

last_pressed = False
def key_clicked(btn_rects):
    global last_pressed
    x, y, pressed = ts.read()
    if pressed:
        for i, btn in enumerate(btn_rects):
            if is_in_button(x, y, btn):
                if not last_pressed:
                    last_pressed = True
                    return True, i, btn
    else:
        last_pressed = False
    return False, 0, []

def show_msg(img:image.Image, msg, dis_size, y=110, diaplay=True, fill = None, scale = 1.2, thickness = -2, color = image.COLOR_RED):
    w, h = image.string_size(msg, scale=scale, thickness = thickness)
    x = int((dis_size[0] - w) // 2)
    if fill:
        img.draw_rect(x, y, w, h, color=fill, thickness=-1)
    img.draw_string(x, y, msg, scale = scale, color = color, thickness = thickness)
    if diaplay:
        disp.show(img)

def draw_center_string(img, msg, dis_size, y=110, diaplay=False, fill = None, scale = 1.2, thickness = -2, color=image.COLOR_RED):
    w, h = image.string_size(msg, scale=scale, thickness = thickness)
    x = int((dis_size[0] - w) // 2)
    if fill:
        img.draw_rect(x, y, w, h, color=fill, thickness=-1)
    img.draw_string(x, int(y), msg, scale = scale, color = color, thickness = thickness)
    if diaplay:
        disp.show(img)

def draw_frame(dis_img, dis_size, key_l = None, key_r = None, icon = None, msg = None, image_offset = (0, 0), msg_y = None, color=image.COLOR_RED):
    if key_l:
        key_l = "| " + key_l
        dis_img.draw_string(2, dis_img.height() - 40, key_l, scale = 1.2, color = image.COLOR_RED, thickness = -1)
    if key_r:
        key_r += " |"
        w = int(dis_size[0] - 2 - image.string_size(key_r)[0] * 1.2)
        dis_img.draw_string(w, dis_img.height() - 40, key_r, scale = 1.2, color = image.COLOR_RED, thickness = -1)
    if icon:
        dis_img.draw_image(image_offset[0], image_offset[1], icon)
        if msg:
            x = int((dis_size[0] - 1.2 * image.string_size(msg)[0]) / 2)
            y = 10 if msg_y is None else msg_y
            dis_img.draw_string(x, y, msg, scale = 1.2, color = image.COLOR_RED, thickness = -1)
    elif msg:
        x = int((dis_size[0] - 1.2 * image.string_size(msg)[0]) / 2)
        y = 10 if msg_y is None else int(msg_y)
        dis_img.draw_string(x, y, msg, scale = 1.2, color = image.COLOR_WHITE, thickness = -1)

def frame_func_select(cam_size, dis_size, func_idx = 0):
    key_l = False
    key_r = False
    upload_img = os.path.join(assets_dir, "upload.png")
    deploy_img = os.path.join(assets_dir, "deployment.png")
    res_img = os.path.join(assets_dir, "resolution.png")
    exit_img = os.path.join(assets_dir, "exit.png")
    funcs = ["collect", "deployment", "resolution", "exit"]
    names = [tr("Collect images"), tr("Deploy model"), tr("Resolution settings"), tr("Exit")]
    upload_img = image.load(upload_img, image.Format.FMT_RGBA8888)
    deploy_img = image.load(deploy_img, image.Format.FMT_RGBA8888)
    res_img = image.load(res_img, image.Format.FMT_RGBA8888)
    exit_img = image.load(exit_img, image.Format.FMT_RGBA8888)
    icons = [upload_img, deploy_img, res_img, exit_img]

    if dis_size[0] == 320:
        icons_pos = [(96, 56), (96, 56), (96, 56), (96, 56), (96, 56), (96, 56)]
    icons_pos = []
    icons_size = [(128, 128), (128, 128), (128, 128), (128, 128), (128, 128), (128, 128)]
    for w, h in icons_size:
        icons_pos.append(((disp.width() - w) // 2, (disp.height() - h) // 2))
    animing = None  # (old_idx, new_idx, pox_x)
    animing_stage = 0
    btn_rects = [
        [0, disp.height() - 60, 80, 60],
        [disp.width() - 80, disp.height() - 60, 80, 60],
    ]
    anime_step = disp.width() // 5
    cam = camera.Camera(cam_size[0], cam_size[1])
    while 1:
        img = cam.read()
        img = img.to_format(image.Format.FMT_RGBA8888)
        clicked, idx, btn_rect = key_clicked(btn_rects)
        if clicked:
            if idx == 1:
                return funcs[func_idx], func_idx
            if idx == 0:
                animing = [func_idx]
                func_idx += 1
                if func_idx >= len(funcs):
                    func_idx = 0
                animing.append(func_idx)
                animing.append(icons_pos[animing[0]][0])
                animing_stage = 0
        dis_img = img.resize(dis_size[0], dis_size[1], image.Fit.FIT_CONTAIN)
        if animing:
            animing[2] -= anime_step
            old_idx, new_idx, pos_x = animing
            # old right to left
            if animing_stage == 0:
                if pos_x <= -icons_size[old_idx][0]:
                    animing_stage = 1
                    animing[2] = dis_size[0]
                    continue
                icon = icons[old_idx] if icons[old_idx] else None
                pos = (pos_x, icons_pos[old_idx][1])
                draw_frame(dis_img, dis_size, tr("func"), tr("ok"), icon, names[old_idx], pos)
            else:
                if pos_x <= icons_pos[new_idx][0]:
                    animing = None
                    continue
                icon = icons[new_idx] if icons[new_idx] else None
                pos = (pos_x, icons_pos[new_idx][1])
                draw_frame(dis_img, dis_size, tr("func"), tr("ok"), icon, names[new_idx], pos)
        else:
            icon = icons[func_idx] if icons[func_idx] else None
            draw_frame(dis_img, dis_size, tr("func"), tr("ok"), icon, names[func_idx], icons_pos[func_idx])
        disp.show(dis_img)
    del cam
    return None, func_idx

def frame_collect(cam_size, dis_size):
    key_l = False
    key_r = False
    cam = camera.Camera(cam_size[0], cam_size[1])
    url = None
    token = None
    status_list = ["init", "scan", "collect", "sure_upload", "upload", "scan_error", "collect_local", "sure_save"]
    status = "init"
    upload_img = None
    start_collect_local = False
    save_count = 1
    btn_rects = [
        [0, disp.height() - 60, 80, 60],
        [disp.width() - 80, disp.height() - 60, 80, 60],
    ]
    def get_new_save_dir():
        save_dir = os.path.join("/root", "collect_pics")
        if not os.path.exists(save_dir):
            save_dir = os.path.join(save_dir, "1")
        else:
            name_id = len(os.listdir(save_dir))
            save_dir = os.path.join(save_dir, str(name_id + 1))
            while os.path.exists(save_dir):
                name_id += 1
                save_dir = os.path.join(save_dir, str(name_id + 1))
        return save_dir

    while 1:
        img = cam.read()
        dis_img = img.resize(dis_size[0], dis_size[1], image.Fit.FIT_CONTAIN)
        # keys
        clicked, idx, btn_rect = key_clicked(btn_rects)
        # first time, show loading
        if status == "init":
            string = tr("Loading") + " ..."
            show_msg(dis_img, string, dis_size)
            status = "scan"
        # no upload url
        if status == "scan":
            if clicked:
                if idx == 0:
                    break
                if idx == 1:
                    status = "collect_local"
                    start_collect_local = True
                    save_dir = get_new_save_dir()
                    save_count = 1
                    continue
            qr_scan_len = max(min(img.width(), img.height()) // 2, min(224, min(img.width(), img.height())))
            qr_scan_zone = ((img.width() - qr_scan_len) // 2, (img.height() - qr_scan_len) //2, qr_scan_len, qr_scan_len)
            img_qr = img.crop(qr_scan_zone[0], qr_scan_zone[1], qr_scan_zone[2], qr_scan_zone[3])
            result = img_qr.find_qrcodes()
            if result:
                try:
                    result = json.loads(result[0].payload())
                    url = result["u"]
                    token = result["k"]
                    _type = result["t"]
                    if _type != "u":
                        print("QR code type error, {} not correct, should be {}".format(_type, "u"))
                        raise Exception("type error")
                except Exception:
                    status = "scan_error"
                    continue
                ok, msg = upload_heartbeat(url, token)
                if not ok:
                    print("Connet server failed:", msg)
                    show_msg(dis_img, tr("Connect failed") + "!", dis_size, y = 130)
                    show_msg(dis_img, msg, dis_size, y = 150)
                    time.sleep(3)
                    status = "scan_error"
                    continue
                status = "collect"
                show_msg(dis_img, tr("Loading") + " ...", dis_size, color=image.COLOR_WHITE)
                time.sleep(0.5)
                continue
            qr_zone = image.resize_map_pos(img.width(), img.height(), dis_img.width(), dis_img.height(), image.Fit.FIT_CONTAIN, qr_scan_zone[0], qr_scan_zone[1], qr_scan_zone[2], qr_scan_zone[3])
            dis_img.draw_rect(qr_zone[0], qr_zone[1], qr_zone[2], qr_zone[3], color=image.COLOR_WHITE, thickness=2)
            msg = tr("Visit") + " maixhub.com"
            draw_frame(dis_img, dis_size, tr("back"), tr("collect locally"), None, tr("Scan QR code"), msg_y = 22 + image.string_size(msg)[1], color=image.COLOR_WHITE)
            draw_center_string(dis_img, msg, dis_size, y = 20, color=image.COLOR_WHITE)
        elif status == "scan_error":
            if clicked and idx == 1:
                status = "scan"
                continue
            draw_frame(dis_img, dis_size, None, tr("ok"), None, tr("QR code error"))
        # collect data and upload
        elif status == "collect":
            if clicked and idx == 1:
                upload_img = img
                status = "sure_upload"
            elif clicked and idx == 0:
                status = "scan"
                continue
            draw_frame(dis_img, dis_size, tr("back"), tr("collect"))
        elif status == "collect_local":
        # need set save_dir and save_count variable
            if clicked and idx == 1:
                upload_img = img
                status = "sure_save"
                start_collect_local = False
                continue
            elif clicked and idx == 0:
                status = "scan"
                continue
            if start_collect_local:
                msg = tr("Will save to")
                w, h = image.string_size(msg, scale = 1, thickness = -1)
                dis_img.draw_string(2, dis_size[1] - h * 3 - 45, msg, scale = 1, color = image.COLOR_RED, thickness = -1)
                dis_img.draw_string(2, dis_size[1] - h * 2 - 45, os.path.join(save_dir, f'{save_count}.jpg'), scale = 1, color = image.COLOR_RED, thickness = -1)
                dis_img.draw_string(2, dis_size[1] - h - 45, tr("Can re-enter to change dir"), scale = 1, color = image.COLOR_RED, thickness = -1)
            else:
                dis_img.draw_string(2, dis_size[1] - h * 2 - 45, msg, scale = 1, color = image.COLOR_RED, thickness = -1)
                dis_img.draw_string(2, dis_size[1] - h - 45, os.path.join(save_dir, f'{save_count}.jpg'), scale = 1, color = image.COLOR_RED, thickness = -1)
            draw_frame(dis_img, dis_size, tr("back"), tr("collect"))
        elif status == "sure_save":
            if clicked and idx == 1:
                if not os.path.exists(save_dir):
                    os.makedirs(save_dir)
                img.save(os.path.join(save_dir, f"{save_count}.jpg"))
                save_count += 1
                status = "collect_local"
                continue
            if clicked and idx == 0:
                status = "collect_local"
                continue
            dis_img = upload_img.copy()
            dis_img = dis_img.resize(dis_size[0], dis_size[1], image.Fit.FIT_CONTAIN)
            draw_frame(dis_img, dis_size, tr("cancel"), tr("save"), None, tr("Save") + " ?")
        elif status == "sure_upload":
            dis_img = upload_img.copy()
            dis_img = dis_img.resize(dis_size[0], dis_size[1], image.Fit.FIT_CONTAIN)
            draw_frame(dis_img, dis_size, tr("cancel"), tr("upload"), None, tr("Upload") + " ?")
            if clicked and idx == 1:
                status = "upload"
            if clicked and idx == 0:
                upload_img = None
                status = "collect"
        elif status == "upload":
            show_msg(dis_img, tr("Uploading") + " ...", dis_size)
            jpg = upload_img.to_jpeg(95).to_bytes()
            ok, msg = upload_dataset(jpg, url, token)
            if not ok:
                print("upload failed:", msg)
                show_msg(dis_img, tr("Upload failed!"), dis_size, y = 130)
                show_msg(dis_img, msg, dis_size, y = 150)
                time.sleep(3)
            upload_img = None
            status = "collect"
        disp.show(dis_img)
    return "func"

def frame_resolution(cam_size, dis_size):
    status_list = ["select", "sure"]
    status = "select"
    final = cam_size
    cam = camera.Camera(cam_size[0], cam_size[1])
    res_list = [(96, 96), (128, 128), (224, 224), (240, 240), (320, 240), (320, 320), (416, 416), (448, 448), (640, 480), (640, 640), (1024, 720), (1920, 1080)]
    names = []
    for item in res_list:
        names.append(f'{item[0]} x {item[1]}')
    res_idx = 2
    for i, size in enumerate(res_list):
        if cam_size[0] == size[0] and cam_size[1] == size[1]:
            res_idx = i
    ui_list = UI_List(names, -1, 60, 5, 1.5, default_idx = res_idx, value_items=res_list)
    while 1:
        img = cam.read()
        dis_img = img.resize(dis_size[0], dis_size[1], image.Fit.FIT_CONTAIN)
        # keys
        btn_rects = [
            [0, disp.height() - 60, 80, 60],
            [disp.width() - 80, disp.height() - 60, 80, 60],
        ]
        clicked, idx, btn_rect = key_clicked(btn_rects)
        if status == "select":
            if clicked:
                if idx == 1:
                    i, item = ui_list.get_selected()
                    if item[0] != final[0] or item[1] != final[1]:
                        status = "sure"
                        continue
                    break # no change
                elif idx == 0:
                    ui_list.next()
                    key_l = False
                    continue
            ui_list.draw(dis_img)
            draw_frame(dis_img, dis_size, tr("switch"), tr("ok back"))
        elif status == "sure":
            if clicked:
                if idx == 0:
                    break
                elif idx == 1:
                    i, item = ui_list.get_selected()
                    final = item
                    break
            draw_frame(dis_img, dis_size, tr("cancel"), tr("save"), None, tr("Sure to change ?"))
        disp.show(dis_img)
    del cam
    return "func", final

def frame_deploy(cam_size, dis_size):
    btn_rects = [
        [0, disp.height() - 60, 80, 60],
        [disp.width() - 80, disp.height() - 60, 80, 60],
    ]
    cam = camera.Camera(cam_size[0], cam_size[1])
    url = None
    token = None
    saved_models_info = []
    ui_model_list = None
    ui_model_sub_list = None
    status_list = ["init", "scan", "get_model", "run", "error", "view_model"]
    status = "init"
    def get_model_info(url, token):
        import requests
        headers = {
            "token": token
        }
        try:
            res = requests.post(url, headers = headers)
            if res.status_code != 200:
                return None, tr("Request server error")
            try:
                res = res.json()
                if res["code"] != 0:
                    print("response code != 0:", res["code"], res["msg"])
                    raise Exception()
            except Exception:
                return None, tr("Response error")
            res = res["data"]
        except Exception:
            return None, tr("Request server error")
        # check args
        args = ["id", "model", "name"]
        for v in args:
            if v not in res:
                return False, tr("Params error!")
        return res, ""

    while 1:
        img = cam.read()
        dis_img = img.resize(dis_size[0], dis_size[1], image.Fit.FIT_CONTAIN)
        # keys
        clicked, idx, btn_rect = key_clicked(btn_rects)
        # first time, show loading
        if status == "init":
            string = tr("Loading") + " ..."
            show_msg(dis_img, string, dis_size)
            status = "scan"
        # no upload url
        if status == "scan":
            if clicked and idx == 0:
                break
            if clicked and idx == 1:
                status = "view_model"
                continue
            qr_scan_len = max(min(img.width(), img.height()) // 2, min(224, min(img.width(), img.height())))
            qr_scan_zone = ((img.width() - qr_scan_len) // 2, (img.height() - qr_scan_len) //2, qr_scan_len, qr_scan_len)
            img_qr = img.crop(qr_scan_zone[0], qr_scan_zone[1], qr_scan_zone[2], qr_scan_zone[3])
            result = img_qr.find_qrcodes()
            if result:
                try:
                    result = json.loads(result[0].payload())
                    url = result["u"]
                    token = result["k"]
                    _type = result["t"]
                    platform = result["p"]
                    if not is_support_model_platform(platform):
                        print("Not support platform")
                        raise Exception("Platform error")
                    if _type != "d":
                        print("QR code type error, {} not correct, should be {}".format(_type, "d"))
                        raise Exception("Type error")
                except Exception:
                    status = "error"
                    err_msg = tr("QR code error")
                    continue
                status = "get_model"
                # dis_img.draw_rect(0, 0, dis_size[0], dis_size[1], color=color_green, thickness=-1)
                show_msg(dis_img, tr("Loading") + " ...", dis_size, color=image.COLOR_WHITE)
                time.sleep(0.5)
                continue
            qr_zone = image.resize_map_pos(img.width(), img.height(), dis_img.width(), dis_img.height(), image.Fit.FIT_CONTAIN, qr_scan_zone[0], qr_scan_zone[1], qr_scan_zone[2], qr_scan_zone[3])
            dis_img.draw_rect(qr_zone[0], qr_zone[1], qr_zone[2], qr_zone[3], color=image.COLOR_WHITE, thickness=2)
            msg = tr("Visit") + " maixhub.com"
            draw_frame(dis_img, dis_size, tr("back"), tr("view saved"), None, tr("Scan QR code"), msg_y = 22 + image.string_size(msg)[1], color=image.COLOR_WHITE)
            draw_center_string(dis_img, msg, dis_size, y = 20, color=image.COLOR_WHITE)
        elif status == "error":
            if clicked and idx == 1:
                status = "scan"
                continue
            draw_frame(dis_img, dis_size, None, tr("ok"), None, err_msg)
        # get model info
        elif status == "get_model":
            bg = image.Color.from_rgb(0, 0, 0)
            dis_img.draw_rect(0, 0, dis_size[0], dis_size[1], color=bg, thickness=-1)
            draw_frame(dis_img, dis_size, tr("cancel"))
            show_msg(dis_img, tr("Get model info") + " ...", dis_size, y = 60, color=image.COLOR_WHITE)
            res, msg = get_model_info(url, token)
            if not res:
                status = "error"
                if msg:
                    err_msg = msg
                else:
                    err_msg = tr("Get model info") + " " + tr("failed")
                continue
            show_msg(dis_img, tr("Downloading model") + " ...", dis_size, y=100, color=image.COLOR_WHITE)
            def on_progress(curr, total):
                download_cancel = False
                # update keys
                clicked, idx, btn_rect = key_clicked(btn_rects)
                if clicked and idx == 0:
                    download_cancel = True
                dis_img.draw_rect(1, 200, dis_img.width() - 2, 20, color=image.COLOR_WHITE, thickness=2)
                dis_img.draw_rect(3, 202, int(curr / total * (dis_img.width() - 2)), 18, color=image.COLOR_WHITE, thickness=-1)
                prog_str = f'{bytes_to_human(curr)} / {bytes_to_human(total)}, {curr / total * 100:.1f}%'
                dis_img.draw_rect(0, 150, dis_img.width(), image.string_size(prog_str)[1] + 20, color=image.COLOR_BLACK, thickness=-1)
                show_msg(dis_img, prog_str, dis_size, y=160, color=image.COLOR_WHITE)
                return download_cancel
            ok, msg = download_file(res["model"], "model.zip", on_progress)
            if not ok:
                status = "error"
                err_msg = tr("Download Failed!") + " " + msg
                continue
            loading_str = tr("Unzip model") + " ..."
            dis_img.draw_rect(0, 150, dis_img.width(), image.string_size(loading_str)[1] + 20, color=image.COLOR_BLACK, thickness=-1)
            show_msg(dis_img, loading_str, dis_size, y=150, color=image.COLOR_WHITE)
            model_dir = f'/root/models/maixhub/{res["id"]}'
            ok, msg = unzip_files("model.zip", model_dir)
            if not ok:
                status = "error"
                err_msg = tr("Unzip Failed!")
                continue
            # save model info to model_info.json
            with open(os.path.join(model_dir, "model_info.json"), "w") as f:
                res.pop("model")
                json.dump(res, f)
            model_init = False
            status = "run"
        elif status == "run":
        # need set var model_dir and set model_init to False
            if not model_init:
                show_msg(dis_img, tr("Loading model") + " ...", dis_size)
                try:
                    model_path, model_type, demo = load_model_info(model_dir)
                except Exception as e:
                    model_path = None; info = ""
                    import traceback; traceback.print_exc()
                if not model_path:
                    status = "error"
                    print(f"Load model {model_dir} failed")
                    err_msg = tr("Load model failed")
                    continue
                cam.set_resolution(demo.input_size()[0], demo.input_size()[1])
                model_init = True
                continue
            demo.loop(img, dis_img, clicked and idx == 1)
            draw_frame(dis_img, dis_size, tr("back"))
            if clicked and idx == 0:
                print("exit run")
                break
        elif status == "view_model":
            if not saved_models_info:
                names = [tr("back")]
                saved_models_info = load_saved_models("/root/models/maixhub")
                for model_info in saved_models_info:
                    names.append(f'{model_info["name"]} ({model_info["model_type"]})')
                ui_model_list = UI_List(names, 20, 50, lines = 7, scale = 1.5, color_active = color_green)
                ui_model_sub_list = None
            draw_frame(dis_img, dis_size, tr("switch"), tr("select"))
            if clicked and idx == 0:
                if not ui_model_sub_list:
                    ui_model_list.next()
                else:
                    ui_model_sub_list.next()
                continue
            if clicked and idx == 1:
                if not ui_model_sub_list:
                    slected_idx, item = ui_model_list.get_selected()
                    if item == tr("back"):
                        status = "scan"
                    else:
                        slected_idx -= 1 # first item is back
                        names = [tr("back"), tr("run"), tr("delete")]
                        ui_model_sub_list = UI_List(names, 160, 100, lines = 3, scale = 1.5,
                                                color = image.Color.from_rgb(102, 102, 102), color_active = color_green,
                                                rectangle = image.COLOR_WHITE)
                else:
                    i, item = ui_model_sub_list.get_selected()
                    if item == tr("back"):
                        ui_model_sub_list = None
                    elif item == tr("run"):
                        status = "run"
                        model_init = False
                        model_dir = saved_models_info[slected_idx]["path"]
                        print("now run", model_dir)
                    elif item == tr("delete"):
                        model_dir = saved_models_info[slected_idx]["path"]
                        if saved_models_info[slected_idx]["is_dir"]:
                            remove_dir(model_dir)
                        else:
                            remove_mud_model(model_dir)
                        ui_model_list.remove(slected_idx + 1)
                        ui_model_sub_list = None
                key_r = False
                continue
            ui_model_list.draw(dis_img)
            if ui_model_sub_list:
                ui_model_sub_list.draw(dis_img)
        disp.show(dis_img)
    del cam
    gc.collect()
    return "func"

def main():
    try:
        board = get_board_name()
        if not board:
            raise Exception("unknown board, maybe you need to upgrade maixhub tool and upgrade maixpy3")
        if board not in ["maixcam"]:
            raise Exception(f"board {board} not support yet")
        dis_size = (disp.width(), disp.height())
        func = "func"
        idx = 0
        params = Params()
        params.load()
        cam_size= params.params["resolution"]
        set_language(i18n.get_locale())
        while 1:
            print(cam_size, dis_size)
            if func == "func":
                func, idx = frame_func_select(cam_size, dis_size, idx)
            elif func == "collect":
                func = frame_collect(cam_size, dis_size)
            elif func == "resolution":
                func, new_cam_size = frame_resolution(cam_size, dis_size)
                if new_cam_size[0] != cam_size[0] or new_cam_size[1] != cam_size[1]:
                    cam_size = new_cam_size
                    params.params["resolution"] = cam_size
                    params.save()
            elif func == "deployment":
                func = frame_deploy(cam_size, dis_size)
            else:
                print("exit")
                break
            gc.collect()
    except Exception as e:
        import traceback
        e = traceback.format_exc()
        print(e)
        img = image.Image(disp.width(), disp.height())
        img.draw_string(2, 2, e, image.COLOR_WHITE, font="hershey_complex_small", scale=0.6)
        disp.show(img)
        while not app.need_exit():
            time.sleep(0.2)
