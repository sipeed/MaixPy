from maix import pinmap, ext_dev, err, time

port = "/dev/ttyS1"
uart_addr = 0x00
uart_baudrate = 115200
step_angle = 18
micro_step = 256
screw_pitch = 3
speed = 6
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

slide = ext_dev.tmc2209.ScrewSlide(port, uart_addr, uart_baudrate,
                            step_angle, micro_step, screw_pitch, speed,
                            use_internal_sense_resistors, run_current_per, hold_current_per)
### or
# slide = ext_dev.tmc2209.ScrewSlide(port, uart_addr, uart_baudrate,
#                             step_angle, micro_step, screw_pitch, speed)

def reset_callback() -> bool:
    if 2 > 1:   # An event occurs (e.g., a sensor is triggered),
                # indicating that the slide has moved to the boundary and the motor needs to stop.
        print("Reset finish...")
        return True
    # Not occurred, no need to stop the motor.
    return False

def move_callback(per:float) -> bool:
    # per is the percentage of the current distance moved by move()
    # out of the total distance required for the current move(), ranging from 0 to 100.
    print(f"Slide moving... {per}")
    if per >= 50: # Example: Stop moving when 50% of the total distance for the current move() has been covered.
        print(f"{per} >= 50%, stop.")
        return True
    return False


slide.reset(reset_callback)

slide.move(screw_pitch*2, -1, move_callback)
slide.move(-screw_pitch)

while True:
    slide.move(screw_pitch*2)
    slide.move(-(screw_pitch*2))
    time.sleep_ms(100)