from maix import comm, protocol, app
from maix.err import Err, check_raise


APP_CMD_ECHO = 0x01

# APP_ID = "my_app1"
# app.set_app_id(APP_ID) # for test, temporary sets app id, DO NOT use it when release(pack) APP.

# init communication object, will init uart or tcp server according to system config
# we can get current setting by maix.app.get_sys_config_kv("comm", "method")
p = comm.CommProtocol(buff_size = 1024)

while not app.need_exit():
    msg = p.get_msg()
    if msg and msg.is_req: # find message and is request
        if msg.cmd == APP_CMD_ECHO:
            resp_msg = "echo from app {}".format(app.app_id())
            p.resp_ok(msg.cmd, resp_msg.encode())
        elif msg.cmd == protocol.CMD.CMD_SET_REPORT:
            p.resp_err(msg.cmd, Err.ERR_NOT_IMPL, "this cmd not support auto upload".encode())

