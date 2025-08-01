from maix import image, camera, display, thread, time, nn, touchscreen, app

disp = display.Display()
img = image.Image(disp.width(), disp.height())
msg = "Loading ..."
size = image.string_size(msg, scale = 1.5, thickness=2)
img.draw_string((img.width() - size.width()) // 2, (img.height() - size.height()) // 2, msg, scale=1.5, thickness=2)
disp.show(img)

from servo_util import Servo
from pid_util import PID
from find_circle import FindRectCircle
import threading

SHOW_DEBUG = True

class Gimbal:
    """Gimbal Class.

    Args:
        pitch (Servos): Pitch servos.
        pid_pitch (PID): Pitch PID.
        roll (None | Servos, optional): Roll servos. Defaults to None.
        pid_roll (None | PID, optional): Roll PID. Defaults to None.
        yaw (None | Servos, optional): Yaw servos. Defaults to None.
        pid_yaw (None | PID, optional): Yaw PID. Defaults to None.
    """
    def __init__(self,  pitch:Servo, pid_pitch:PID,
                        roll:None|Servo=None, pid_roll:None|PID=None,
                        yaw:None|Servo=None, pid_yaw:None|PID=None):
        self._pitch = pitch
        self._roll = roll
        self._yaw = yaw
        self._pid_pitch = pid_pitch
        self._pid_roll = pid_roll
        self._pid_yaw = pid_yaw

    def run(self, pitch_err:float, roll_err:float=0, yaw_err:float=0,
            pitch_reverse:bool=False, roll_reverse:bool=False, yaw_reverse:bool=False):
        """Perform the Gimbal operation.

        Args:
            pitch_err (float): Pitch error.
            roll_err (float, optional): Roll error. Defaults to 0.
            yaw_err (float, optional): Yaw error. Defaults to 0.
            pitch_reverse (bool, optional): Pitch reverse. Defaults to False.
            roll_reverse (bool, optional): Roll reverse. Defaults to False.
            yaw_reverse (bool, optional): Yaw reverse. Defaults to False.
        """
        out = self._pid_pitch.get_pid(pitch_err, 1)
        if SHOW_DEBUG:
            print(f"pitch err:{round(pitch_err, 2)}, pid_out:{round(out,2)}", end = ", ")
        if pitch_reverse:
            out = - out
        self._pitch.drive(out)
        if self._roll:
            out = self._pid_roll.get_pid(roll_err, 1)
            if SHOW_DEBUG:
                print(f"roll_err:{round(roll_err,2):6.2f}, pid_out:{round(out,2):6.2f}", end = ", ")
            if roll_reverse:
                out = - out
            self._roll.drive(out)
        if self._yaw:
            out = self._pid_yaw.get_pid(yaw_err, 1)
            if SHOW_DEBUG:
                print(f"yaw_err:{yaw_err:6.2f}, pid_out:{out:6.2f}", end="")
            if yaw_reverse:
                out = - out
            self._yaw.drive(out)
        if SHOW_DEBUG:
            print("")

class Target:
    """Obtain the error value between the target and the center point.
       Need to modify __init__() and __get_target().
    Args:
        out_range_pitch (float): output range, e.g. 10 means output range is [-10, 10].
        out_range_yaw (float): output range, e.g. 10 means output range is [-10, 10].
        ignore_limit (float): dead zone, when error < out_range * ignore_limit, set error to 0
        path (str): model path
    """
    def __init__(self, out_range_pitch:float, out_range_yaw:float, ignore_limit:float, disp:display.Display):
        """Constructor
            Initialization of the recognition model class or other classes needs to be implemented here.
        """
        self.pitch = 0
        self.yaw = 0
        self.out_range_pitch = out_range_pitch
        self.out_range_yaw = out_range_yaw
        self.ignore = ignore_limit

        self.finder = FindRectCircle(disp)
        self.w, self.h = self.finder.get_res()


    def _get_target_err_pixels(self):
        circle_center, screen_center, err_center, circle3, update = self.finder.run()
        return err_center

    def get_target_err(self):
        err_x, err_y = self._get_target_err_pixels()
        # pixels to percentage
        self.pitch  = err_y / self.h * self.out_range_pitch
        self.yaw    = err_x / self.w * self.out_range_yaw
        if abs(self.pitch) < self.out_range_pitch * self.ignore:
            self.pitch = 0
        if abs(self.yaw) < self.out_range_yaw * self.ignore:
            self.yaw = 0
        return self.pitch, self.yaw


# class UI:
#     def __init__(self, disp):
#         self.ts = touchscreen.TouchScreen()
#         self.img_exit = image.load("/maixapp/share/icon/ret.png")
#         self.disp = disp.add_channel()
#         self.ts = touchscreen.TouchScreen()
#         self.img_back = image.load("/maixapp/share/icon/ret.png")
#         self.back_rect = [0, 0, self.img_back.width(), self.img_back.height()]
#         self.img = image.Image(self.disp.width(), self.disp.height(), image.Format.FMT_RGBA8888, bg = image.Color.from_rgba(0, 0, 0, 1))
#         self.img.draw_image(0, 0, self.img_back)
#         self.disp.show(self.img)


#     def run(self):
#         # self.disp.show()
#         # time.sleep_ms(50) # release CPU
#         self.disp.show(self.img)
#         pass

# def run_ui(disp):
#     # initialize UI
#     ui = UI(disp)
#     while not app.need_exit():
#         ui.run()


def main(disp):
    pitch_pin = "A18"
    yaw_pin = "A19"
    servo_freq = 50                # 50Hz 20ms
    # pitch_duty_range = [2.5, 7.5]  # [2.5%,  7.5%] <--> [0.5ms, 1.5ms]
    # yaw_duty_range = [2.5, 12.5]   # [2.5%, 12.5%] <--> [0.5ms, 2.5ms]
    pitch_duty_range = [5, 7.5]      # 根据实际舵机旋转范围修改以限制旋转角度
    yaw_duty_range = [3.5, 12.5]     # 根据实际舵机旋转范围修改以限制旋转角度
    pitch_init_angle = 50          # init position, unit is percentage, value: [0, 100]
    yaw_init_angle = 50            # init position, unit is percentage, value: [0, 100]
    pitch_pid = [1.5, 0.0001, 0.2, 0]    # [P I D I_max]
    yaw_pid  = [0.5, 0.0001, 0.05, 0]     # [P I D I_max]
    target_err_range_pitch = 10          # target error output range, bigger value will make error bigger so move faster.
    target_err_range_yaw = 10            # target error output range, bigger value will make error bigger so move faster.
    target_ignore_limit = 0.02           # when target error < target_err_range*target_ignore_limit , set target error to 0
    pitch_reverse = False                # reverse out value direction
    yaw_reverse = True                   # reverse out value direction

    # initialize servos
    pitch = Servo(pitch_pin, pitch_init_angle, pitch_duty_range, freq=servo_freq)
    yaw = Servo(yaw_pin, yaw_init_angle, yaw_duty_range, freq=servo_freq)

    # initialize target
    target = Target(target_err_range_pitch, target_err_range_yaw, target_ignore_limit, disp)

    # initialize PID
    pid_pitch = PID(*pitch_pid)
    pid_yaw = PID(*yaw_pid)
    gimbal = Gimbal(pitch, pid_pitch, None, None, yaw, pid_yaw)


    # new thread show UI, have BUG, so remove
    # ui_thread = threading.Thread(target=run_ui, args=(disp,))
    # ui_thread.daemon = True
    # ui_thread.start()

    ltime = time.ticks_ms()
    while not app.need_exit():
        # loop interval limit to >= 10ms
        if time.ticks_ms() - ltime < 10:
            continue
        ltime = time.ticks_ms()

        # recognize target and get error
        err_pitch, err_yaw = target.get_target_err()

        # run PID controller
        gimbal.run(err_pitch, 0, err_yaw, pitch_reverse=pitch_reverse, yaw_reverse=yaw_reverse)

        # time.sleep_us(500) # release CPU


if __name__ == '__main__':
    try:
        while not app.need_exit():
            main(disp)
    except Exception:
        import traceback
        msg = traceback.format_exc()
        print(msg)
        img = image.Image(disp.width(), disp.height())
        img.draw_string(0, 0, msg, image.COLOR_WHITE)
        disp.show(img)
        while not app.need_exit():
            time.sleep_ms(100)
