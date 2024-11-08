from maix.comm import modbus
from maix import app, err

slave = modbus.Slave(
    mode=modbus.Mode.RTU,                       # mode
    ip_or_device="/dev/ttyS0",                  # serial device
    coils_start=0x00,       coils_size=10,      # coils
    discrete_start=0x00,    discrete_size=10,   # discrete input
    holding_start=0x00,     holding_size=10,    # input registers
    input_start=0x00,       input_size=10,      # holding registers
    rtu_baud=115200,        rtu_slave=1,        # serial 115200-8N1, slave
    debug=False                                 # tcp port, debug OFF
)


old_ir = slave.input_registers()
print("old ir: ", old_ir)
data : list[int] = [0x22, 0x33, 0x44]
slave.input_registers(data, 3)
new_ir = slave.input_registers()
print("new ir:", new_ir)

while not app.need_exit():
    if err.Err.ERR_NONE != slave.receive(2000): #timeout 2000ms
        continue

    rtype = slave.request_type()
    if rtype == modbus.RequestType.READ_HOLDING_REGISTERS:
        print("master read hr")
        hr = slave.holding_registers()
        print("now hr: ", hr)
        hr = [x+1 for x in hr]
        print("now we make hr+1: ", hr)
        print("update hr")
        slave.holding_registers(hr)

    slave.reply()


