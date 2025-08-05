'''
    IMU AHRS application
    @license MIT
    @author neucrack@sipeed
    @date 2025.7.8
'''
from maix import image, display, app, time, ahrs, touchscreen
from maix.ext_dev import imu
import math

def is_in_button(x, y, btn_pos):
    return x > btn_pos[0] and x < btn_pos[0] + btn_pos[2] and y > btn_pos[1] and y < btn_pos[1] + btn_pos[3]

def render_pose(pitch, roll, yaw, radian=False):
    if not radian:
        # DEG2RAD = math.pi / 180
        pitch *= ahrs.DEG2RAD
        roll *= ahrs.DEG2RAD
        yaw *= ahrs.DEG2RAD

    # Rotation matrices
    cp, sp = math.cos(pitch), math.sin(pitch)
    cr, sr = math.cos(roll), math.sin(roll)
    cy, sy = math.cos(yaw), math.sin(yaw)

    # ZYX rotation: R = Rz * Ry * Rx
    R = [
        [cy * cr, cy * sr * sp - sy * cp, cy * sr * cp + sy * sp],
        [sy * cr, sy * sr * sp + cy * cp, sy * sr * cp - cy * sp],
        [-sr,     cr * sp,                cr * cp]
    ]

    # Unit axis rotated
    x_rot = [R[0][0], R[1][0], R[2][0]]
    y_rot = [R[0][1], R[1][1], R[2][1]]
    z_rot = [R[0][2], R[1][2], R[2][2]]

    return [(x_rot[0], x_rot[2]), (y_rot[0], y_rot[2]), (z_rot[0], z_rot[2])]


def draw_image(img, angle, dir_cam=False):
    len_ratio = 0.35
    min_edge = min(img.width(), img.height())
    obj_len = min_edge * len_ratio
    offset_x = img.width() * 0.5
    offset_y = img.height() * 0.5
    pose = render_pose(angle.x, angle.y, angle.z, False)

    # scale and transform
    v = []
    for p in pose:
        x = p[0] * obj_len + offset_x
        y = img.height() - (p[1] * obj_len + offset_y)
        v.append((x, y))

    if dir_cam:
        img.draw_line(int(offset_x), int(img.height() - offset_y), int(v[1][0]), int(v[1][1]), image.COLOR_RED, 5)
        img.draw_line(int(v[2][0]), int(v[2][1]), int(v[0][0]), int(v[0][1]), image.COLOR_GRAY, 1)
        img.draw_line(int(offset_x), int(img.height() - offset_y), int(v[0][0]), int(v[0][1]), image.COLOR_WHITE, 5)
        img.draw_line(int(offset_x), int(img.height() - offset_y), int(v[2][0]), int(v[2][1]), image.COLOR_GREEN, 5)
    else:
        img.draw_line(int(v[1][0]), int(v[1][1]), int(v[0][0]), int(v[0][1]), image.COLOR_GRAY, 1)
        img.draw_line(int(offset_x), int(img.height() - offset_y), int(v[1][0]), int(v[1][1]), image.COLOR_RED, 5)
        img.draw_line(int(offset_x), int(img.height() - offset_y), int(v[0][0]), int(v[0][1]), image.COLOR_WHITE, 5)
        img.draw_line(int(offset_x), int(img.height() - offset_y), int(v[2][0]), int(v[2][1]), image.COLOR_GREEN, 5)

    img.draw_string(int(v[0][0]), int(v[0][1]), "x", image.COLOR_WHITE, 1.5)
    img.draw_string(int(v[1][0]), int(v[1][1]), "y", image.COLOR_RED, 1.5)
    img.draw_string(int(v[2][0]), int(v[2][1]), "z", image.COLOR_GREEN, 1.5)

def show_msg(disp, msg):
    img = image.Image(disp.width(), disp.height())
    size = image.string_size(msg, 1.5)
    x = (img.width() - size.width()) // 2
    y = (img.height() - size.height()) // 2
    img.draw_string(x, y, msg, image.COLOR_WHITE, 1.5)
    disp.show(img)

def main(disp):
    ts = touchscreen.TouchScreen()

    kp, ki = 2, 0.01
    pitch_offset = 0
    dir_btn_name = "x dir"
    calib_btn_name = "Calibrate"
    calib_font_size = image.string_size(calib_btn_name)
    dir_font_size = image.string_size(dir_btn_name)

    calib_btn = [disp.width() - 100, disp.height() - 50, 100, 50]
    ret_btn = [0, disp.height() - 50, 100, 50]
    dir_btn = [disp.width() // 2 - dir_font_size.width() // 2 - 10, disp.height() - 50, dir_font_size.width() + 20, 50]

    try:
        sensor = imu.IMU("default")
    except Exception:
        img = image.Image(disp.width(), disp.height())
        msg = "Init IMU failed, maybe no IMU"
        size = image.string_size(msg, scale=1.2, font="hershey_complex_small")
        img.draw_string((img.width() - size.width()) // 2, (img.height() - size.height()) // 2 , msg, image.COLOR_WHITE, scale=1.2, font="hershey_complex_small")
        disp.show(img)
        while not app.need_exit():
            time.sleep(0.2)
        return 0
    filter = ahrs.MahonyAHRS(kp, ki)

    # if not sensor.calib_gyro_exists():
    #     print("Calibrating gyro...")
    #     sensor.calib_gyro(10000)
    # else:
    sensor.load_calib_gyro()

    ts_last = False
    last_time = time.ticks_s()
    while not app.need_exit():
        ts_x, ts_y, ts_pressed = ts.read()

        data = sensor.read_all(calib_gryo=True, radian=True)
        now = time.ticks_s()
        dt = now - last_time
        last_time = now
        angle = filter.get_angle(data.acc, data.gyro, data.mag, dt, radian=False)

        # make y axis same with camera(x rotate 90 degree)
        angle.x -= pitch_offset

        img = image.Image(disp.width(), disp.height())
        img.draw_string(2, 4, f"pitch: {angle.x:.2f}, roll: {angle.y:.2f}, yaw: {angle.z:.2f}", image.COLOR_WHITE, 1.5)
        img.draw_string(2, 36, f"dt: {int(dt * 1000):3d}ms, temp: {data.temp:.1f}", image.COLOR_WHITE, 1.5)
        draw_image(img, angle, pitch_offset == 90)

        img.draw_rect(*calib_btn, image.COLOR_WHITE, 2)
        img.draw_string(calib_btn[0] + 10, calib_btn[1] + (calib_btn[3] - calib_font_size.height()) // 2, calib_btn_name)
        img.draw_rect(*ret_btn, image.COLOR_WHITE, 2)
        img.draw_string(ret_btn[0] + 10, ret_btn[1] + (ret_btn[3] - calib_font_size.height()) // 2, "< Exit")
        img.draw_rect(*dir_btn, image.COLOR_WHITE, 2)
        img.draw_string(dir_btn[0] + 10, dir_btn[1] + (dir_btn[3] - calib_font_size.height()) // 2, dir_btn_name)

        disp.show(img)

        if ts_pressed and is_in_button(ts_x, ts_y, ret_btn):
            break
        elif ts_pressed and not ts_last and is_in_button(ts_x, ts_y, dir_btn):
            pitch_offset = 90 if pitch_offset == 0 else 0
        elif ts_pressed and not ts_last and is_in_button(ts_x, ts_y, calib_btn):
            for i in range(6, 0, -1):
                show_msg(disp, f"Place on desk, don't move.\nStart in {i}s")
                time.sleep(1)
            show_msg(disp, "Calibrating... Don't move\nWait 10s")
            sensor.calib_gyro(10000)
            filter.reset()
            last_time = time.ticks_s()

        ts_last = ts_pressed

        # make sure loop interval > 1ms
        # while time.ticks_s() - last_time < 0.001:
        #     time.sleep_us(100)

if __name__ == '__main__':
    disp = display.Display()
    try:
        main(disp)
    except Exception:
        import traceback
        e = traceback.format_exc()
        print(e)
        img = image.Image(disp.width(), disp.height())
        img.draw_string(2, 2, e, image.COLOR_WHITE, font="hershey_complex_small", scale=0.6)
        disp.show(img)
        while not app.need_exit():
            time.sleep(0.2)
