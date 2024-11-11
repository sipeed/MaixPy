from maix import pinmap, app, err, time, thread
from maix.comm import modbus


REGISTERS_START_ADDRESS = 0x00
REGISTERS_NUMBER = 10

RTU_SLAVE_ID = 1
RTU_BAUDRATE = 115200

def master_thread(*args):
    if pinmap.set_pin_function("A19", "UART1_TX") != err.Err.ERR_NONE:
        print("init uart1 failed!")
        exit(-1)
    if pinmap.set_pin_function("A18", "UART1_RX") != err.Err.ERR_NONE:
        print("init uart1 failed!")
        exit(-1)

    # modbus.set_master_debug(True)

    master = modbus.MasterRTU(
        "/dev/ttyS1",
        RTU_BAUDRATE
    )

    while not app.need_exit():
        hr = master.read_holding_registers(
            RTU_SLAVE_ID,
            REGISTERS_START_ADDRESS,
            REGISTERS_NUMBER,
            2000
        )
        if len(hr) == 0:
            continue
        print("Master read hr: ", hr)
        time.sleep(1)

master_thread(None)