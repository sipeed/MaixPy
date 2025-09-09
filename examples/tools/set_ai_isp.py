from maix import app, err

def get_ai_isp_on():
    ai_isp_on = False if app.get_sys_config_kv("npu", "ai_isp", "0") == "0" else True
    return ai_isp_on

def set_ai_isp(on : bool):
    print("Now set AI ISP: " + ("ON" if on else "OFF"))
    value = "1" if on else "0"
    e = app.set_sys_config_kv("npu", "ai_isp", value)
    err.check_raise(e, f"Set ai isp to {value} failed")


# set_on = True
set_on = False

print("AI ISP :", "ON" if get_ai_isp_on() else "OFF")
set_ai_isp(set_on)
print("AI ISP :", "ON" if get_ai_isp_on() else "OFF")



