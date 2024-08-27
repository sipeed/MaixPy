from maix import ext_dev, pinmap, err

port = "/dev/ttyS1"
uart_addr = 0x00
uart_baudrate = 115200
step_angle = 1.8
micro_step = 256
round_mm = 60
speed = 60
use_internal_sense_resistors = True
run_current_per = 100
hold_current_per = 100

if port == "/dev/ttyS1":
    ret = pinmap.set_pin_function("A19", "UART1_TX")
    if ret != err.Err.ERR_NONE:
        print("Failed in function pinmap...")
        exit(-1)
    ret = pinmap.set_pin_function("A18", "UART1_RX")
    if ret != err.Err.ERR_NONE:
        print("Failed in function pinmap...")
        exit(-1)

ext_dev.tmc2209.slide_test(port, uart_addr, uart_baudrate,
                           step_angle, micro_step, round_mm, speed, True,
                           True, run_current_per, hold_current_per,
                           conf_save_path='./slide_scan_example.bin')