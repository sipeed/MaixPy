from maix.comm import modbus
from maix import app, err

slave = modbus.Slave(
    modbus.Mode.TCP,    # mode
    "",                 # ip, keep empty
    0x00, 10,           # coils
    0x00, 10,           # discrete input
    0x00, 10,           # input registers
    0x00, 10,           # holding registers
    0, 1,               # serial 115200-8N1, slave, ignore
    502, False            # tcp port, debug OFF
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


