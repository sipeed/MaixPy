import struct
from maix import camera, display, image, nn, app
from maix import comm, protocol
from maix.err import Err

detector = nn.YOLOv5(model="/root/models/yolov5s.mud")

cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
disp = display.Display()

APP_CMD_ECHO = 0x01
APP_CMD_DETECT_RES = 0x02

report_on = True


def encode_objs(objs):
    '''
        encode objs info to bytes body for protocol
        2B x(LE) + 2B y(LE) + 2B w(LE) + 2B h(LE) + 2B idx ...
    '''
    body = b''
    for obj in objs:
        body += struct.pack("<hhHHH", obj.x, obj.y, obj.w, obj.h, obj.class_id)
    return body

def decode_objs(body):
    '''
    Decode bytes body back into object information according to the specified protocol.
    Each object is encoded as 2 bytes x (signed, LE), 2 bytes y (signed, LE), 2 bytes w (unsigned, LE),
    2 bytes h (unsigned, LE), and 2 bytes class_id (unsigned, LE).
    '''
    objs = []
    i = 0
    obj_size = struct.calcsize("<hhHHH")  # Calculate the size of each object's data block

    while i < len(body):
        # Unpack the data according to the specified format
        x, y, w, h, class_id = struct.unpack_from("<hhHHH", body, i)
        objs.append({'x': x, 'y': y, 'w': w, 'h': h, 'class_id': class_id})
        i += obj_size  # Move the index to the start of the next object

    return objs


# init communication object, will init uart or tcp server according to system config
# we can get current setting by maix.app.get_sys_config_kv("comm", "method")
p = comm.CommProtocol(buff_size = 1024)

while not app.need_exit():
    # recive and decode message from pair
    msg = p.get_msg()
    if msg and msg.is_req: # find message and is request
        if msg.cmd == APP_CMD_ECHO:
            resp_msg = "echo from app {}".format(app.app_id())
            p.resp_ok(msg.cmd, resp_msg.encode())
        elif msg.cmd == protocol.CMD.CMD_SET_REPORT:
            body = msg.get_body()
            report_on = body[0] == 1 # first byte of body is 0x01 means auto report, else disable report
            resp_body = b'\x01' # 0x01 means set ok
            p.resp_ok(msg.cmd, resp_body)
    elif msg and msg.is_report and msg.cmd == APP_CMD_DETECT_RES:
        print("receive objs:", decode_objs(msg.get_body()))
        p.resp_ok(msg.cmd, b'1')

    # detect objects
    img = cam.read()
    objs = detector.detect(img, conf_th = 0.5, iou_th = 0.45)
    # encode objs info and send
    if len(objs) > 0 and report_on:
        body = encode_objs(objs)
        p.report(APP_CMD_DETECT_RES, body)
    # draw on screen
    for obj in objs:
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color = image.COLOR_RED)
        msg = f'{detector.labels[obj.class_id]}: {obj.score:.2f}'
        img.draw_string(obj.x, obj.y, msg, color = image.COLOR_RED)
    disp.show(img)
