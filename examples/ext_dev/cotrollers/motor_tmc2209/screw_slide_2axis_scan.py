from maix import ext_dev, display, camera, pinmap, time, err, app
import threading

### MODE
MODE_SHOW_PICTURE = 0
MODE_SHOW_VIDEO = 1

# If you have high frame requirement,
# please use cdk, refer to MaixCDK/example/maix_tmc2209_2axis_scan.

### Change mode according to your needs
MODE = MODE_SHOW_PICTURE

if __name__ == "__main__":

    if MODE == MODE_SHOW_PICTURE:
        print("Mode: show picture")
    elif MODE == MODE_SHOW_VIDEO:
        print("Mode: show video")
    else:
        print("Error Mode: ", MODE)
        exit(-1)

    cam = camera.Camera(512, 320)
    disp = display.Display()

    port = "/dev/ttyS1"
    uart_baudrate = 115200

    uart_addr_x = 0x00
    step_angle_x = 18
    micro_step_x = 256
    screw_pitch_x = 3.0
    speed_x = 1.0
    dir_x = True
    start_x = 0
    stop_x = 20
    step_x = 3

    uart_addr_y = 0x03
    step_angle_y = 18
    micro_step_y = 256
    screw_pitch_y = 3.0
    speed_y = 1.0
    dir_y = False
    start_y = 0
    stop_y = 15
    step_y = 3

    if pinmap.set_pin_function("A19", "UART1_TX") != err.Err.ERR_NONE:
        print("pinmap error!")
        exit(-1)
    if pinmap.set_pin_function("A18", "UART1_RX") != err.Err.ERR_NONE:
        print("pinmap error!")
        exit(-1)

    slide_x = ext_dev.tmc2209.ScrewSlide(
        port,
        uart_addr_x,
        uart_baudrate,
        step_angle_x,
        micro_step_x,
        screw_pitch_x,
        speed_x
    )

    slide_y = ext_dev.tmc2209.ScrewSlide(
        port,
        uart_addr_y,
        uart_baudrate,
        step_angle_y,
        micro_step_y,
        screw_pitch_y,
        speed_y
    )

    need_exit = False

    def one_step_callback():
        global need_exit, cam, disp
        img = cam.read()
        disp.show(img)
        return need_exit

    def thread_func():
        while not app.need_exit():
            if one_step_callback():
                break


    if MODE == MODE_SHOW_VIDEO:
        th = threading.Thread(target=thread_func)
        th.daemon = True
        th.start()

    current_x = start_x if dir_x else stop_x
    current_y = start_y if dir_y else stop_y

    dir_x_ = dir_x

    for i in range(0, (stop_y-start_y)//step_y+1):
        target_move_y = step_y if i != 0 else 0
        target_move_y = target_move_y if dir_y else -target_move_y
        slide_y.move(target_move_y)
        current_y = current_y + step_y if dir_y else current_y - step_y

        for j in range(0, (stop_x-start_x)//2):
            target_move_x = step_x if dir_x_ else -step_x
            slide_x.move(target_move_x)
            current_x += target_move_x
            if MODE == MODE_SHOW_PICTURE:
                one_step_callback()
            if app.need_exit():
                break

        dir_x_ = False if dir_x_ else True
        if app.need_exit():
            break

    need_exit = True

    time.sleep(3)