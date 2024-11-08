"""

UART1 TX <-----> UART0 RX
UART1 RX <-----> UART0 TX

"""


from maix import pinmap, app, err, time
from maix.comm import modbus
import threading

def master_thread():
    if pinmap.set_pin_function("A19", "UART1_TX") != err.Err.ERR_NONE:
        print("init uart1 failed!")
        exit(-1)
    if pinmap.set_pin_function("A18", "UART1_RX") != err.Err.ERR_NONE:
        print("init uart1 failed!")
        exit(-1)

    master = modbus.Master(
        mode=modbus.Mode.RTU,
        ip_or_device="/dev/ttyS1",
        rtu_baud=115200,
        rtu_slave=1,
        debug=False
    )

    while not app.need_exit():
        hr = master.read_holding_registers(size=10, addr=0x00, timeout_ms=1000)
        # if len(hr) == 0:
        #     continue
        print("Master read hr: ", hr)
        time.sleep(1)

def slave_thread():
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

    while not app.need_exit():
        if err.Err.ERR_NONE != slave.receive(2000): #timeout 2000ms
            continue

        rtype = slave.request_type()

        if rtype == modbus.RequestType.READ_HOLDING_REGISTERS:
            hr = slave.holding_registers()
            hr = [x+1 for x in hr]
            slave.holding_registers(hr)
            print("--------------------------------------")
            print("Slave update hr: ", hr)

        slave.reply()

slave_th = threading.Thread(target=slave_thread)
slave_th.start()

time.sleep(1)

master_th = threading.Thread(target=master_thread)
master_th.start()

slave_th.join()
master_th.join()