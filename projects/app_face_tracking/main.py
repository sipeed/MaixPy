from face_tracking import servos
from maix import image, camera, display, time, nn, touchscreen

### model path
MODEL = "/root/models/retinaface.mud"



class Target:
    """Obtain the error value between the target and the center point.
       Need to modify __init__() and __get_target().
    Args:
        out_range (float): output range
        ignore_limit (float): dead zone
        path (str): model path
    """
    def __init__(self, out_range:float, ignore_limit:float, path:str):
        """Constructor
            Initialization of the recognition model class or other classes needs to be implemented here.
        """
        self.pitch = 0
        self.roll = 0
        self.out_range = out_range
        self.ignore = ignore_limit
        
        ### Self.w and self.h must be initialized.
        self.detector = nn.Retinaface(model=path)
        self.w = self.detector.input_width()
        self.h = self.detector.input_height()
        self.cam = camera.Camera(self.w, self.h)
        self.disp = display.Display()
        
        ### The following section is used as an opt-out and normally you do not need to modify it.
        self.ts = touchscreen.TouchScreen()
        self.img_exit = image.load("./assets/exit.jpg").resize(40, 40)
        self.img_exit_touch = image.load("./assets/exit_touch.jpg").resize(40, 40)
        self.box = [0, 0, self.img_exit.width(), self.img_exit.height()]
        self.need_exit = False
        
    def __check_touch_box(self, t, box, oft = 0):
        """This method is used for exiting and you normally do not need to modify or call it.
            You usually don't need to modify it.
        """
        if t[2] and t[0] + oft > box[0] and t[0] < box[0] + box[2] + oft and t[1] + oft > box[1] and t[1] < box[1] + box[3] + oft:
            return True
        else:
            return False
    
    def __exit_listener(self, img):
        """Exit case detection methods.
            It also draws the Exit button in the upper left corner.
            You usually don't need to modify it.

        Args:
            img (image.Image): The image that needs to be drawn.
        """
        t = self.ts.read()
        if self.__check_touch_box(t, self.box, 20):
            img.draw_image(self.box[0], self.box[1], self.img_exit_touch)
            self.need_exit = True
        else:
            img.draw_image(self.box[0], self.box[1], self.img_exit)
            
    def is_need_exit(self):
        """Queries whether the exit button has been pressed.
            You usually don't need to modify it.

        Returns:
            bool: Returns true if the exit button has been pressed, false otherwise.
        """
        return self.need_exit
        
    def __get_target(self):
        """Get the coordinate value of the target.
            The behavior of this function needs to be customized.
        Returns:
            int, int: If no target is found, return -1,-1.
                      If the target is found, return the coordinate values x,y of the center point of the target.
        """    
        ltime = time.ticks_ms()
        img = self.cam.read()               # Reads an image frame.
        objs = self.detector.detect(img, conf_th = 0.4, iou_th = 0.45)  # Recognition.
        for obj in objs:                    # Find objects.
            img.draw_rect(obj.x, obj.y, obj.w, obj.h, image.COLOR_RED, 2)
            cent_x = obj.x + round(obj.w/2) # Calculate the x-coordinate of the target center point.
            cent_y = obj.y + round(obj.h/2) # Calculate the y-coordinate of the target center point.
            img.draw_rect(cent_x-1, cent_y-1, 2, 2, image.COLOR_GREEN)
            rtime = time.ticks_ms()
            # print(f"find target used time:{round(rtime-ltime,2)}ms")
            self.__exit_listener(img)       # Queries whether the Exit button was pressed.
            self.disp.show(img)             # Display this image.
            return cent_x, cent_y           # Return (x, y)
        self.__exit_listener(img)
        self.disp.show(img)
        return -1, -1                       # Target not found. Return (-1, -1)

    def get_target_err(self):
        """Obtain the error value between the target and the center point.
            You usually don't need to modify it.

        Returns:
            int, int: y-axis error value, x-axis error value.
        """
        cent_x, cent_y = self.__get_target()
        if cent_x == -1:
            return (0, 0)
        self.pitch = cent_y / self.h * self.out_range * 2 - self.out_range
        self.roll = cent_x / self.w * self.out_range * 2 - self.out_range
        if abs(self.pitch) < self.out_range*self.ignore:
            self.pitch = 0
        if abs(self.roll) < self.out_range*self.ignore:
            self.roll = 0
        return self.pitch, self.roll
          

if __name__ == '__main__':
    ROLL_PWM_PIN_NAME = "A17"   
    PITCH_PWM_PIN_NAME = "A16"
    init_pitch = 80             # init position, value: [0, 100], means minimum angle to maxmum angle of servo
    init_roll = 50              # 50 means middle
    PITCH_DUTY_MIN  = 3.5       # The minimum duty cycle corresponding to the range of motion of the y-axis servo.
    PITCH_DUTY_MAX  = 9.5       # Maximum duty cycle corresponding to the y-axis servo motion range.
    ROLL_DUTY_MIN   = 2.5       # Minimum duty cycle for x-axis servos.
    ROLL_DUTY_MAX   = 12.5      # Maxmum duty cycle for x-axis servos.
    
    pitch_pid = [0.3, 0.0001, 0.0018, 0]    # [P I D I_max]
    roll_pid  = [0.3, 0.0001, 0.0018, 0]    # [P I D I_max]
    target_err_range = 10                   # target error output range, default [0, 10]
    target_ignore_limit = 0.08              # when target error < target_err_range*target_ignore_limit , set target error to 0
    pitch_reverse = False                   # reverse out value direction
    roll_reverse = True                     # reverse out value direction
    
    target = Target(target_err_range, target_ignore_limit, MODEL)
    try:
        roll = servos.Servos(ROLL_PWM_PIN_NAME, init_roll, ROLL_DUTY_MIN, ROLL_DUTY_MAX)
        pitch = servos.Servos(PITCH_PWM_PIN_NAME, init_pitch, PITCH_DUTY_MIN, PITCH_DUTY_MAX)
    except RuntimeError as e:
        print(f"!!!!!!!!!!!!!!!! ERROR: {e} !!!!!!!!!!!!!!!!!!!!!!")
        wait_time_s = 10
        while wait_time_s:
            eimg = image.Image(target.w, target.h)
            eimg.draw_string(10, 10, "Error: "+str(e)+
                             f".   This program will exit after {wait_time_s}s.")
            target.disp.show(eimg)
            time.sleep(1)
            wait_time_s -= 1
        exit(-1)
    
    pid_pitch = servos.PID(p=pitch_pid[0], i=pitch_pid[1], d=pitch_pid[2], imax=pitch_pid[3])
    pid_roll = servos.PID(p=roll_pid[0], i=roll_pid[1], d=roll_pid[2], imax=roll_pid[3])
    gimbal = servos.Gimbal(pitch, pid_pitch, roll, pid_roll)
    
    total_uesd_time = 0
    total_fps = 0
    t0 = time.ticks_ms()
    while not target.is_need_exit():
        ltime = time.ticks_ms()
        
        # get target error
        err_pitch, err_roll = target.get_target_err()
        # interval limit to >= 10ms
        if time.ticks_ms() - t0 < 10:
            continue
        t0 = time.ticks_ms()
        # run
        gimbal.run(err_pitch, err_roll, pitch_reverse = pitch_reverse, roll_reverse=roll_reverse)

        # Calculate FPS.
        rtime = time.ticks_ms()
        utime = rtime-ltime
        total_uesd_time += utime
        total_fps += 1
        print(f"used time:{utime}ms, fps:{round(1000/(utime),2)}, avg_fps:{round(total_fps*1000/total_uesd_time, 2)}")
