"""
Reference: https://maixhub.com/share/1
"""
from maix import pwm, pinmap, time
from math import pi
import logging

logging.basicConfig(level=logging.INFO)

class Servos:
    """Servo control class

    Args:
        pwm_pin (str): PWM pin to be used, e.g. “A17”.
        dir (float): Initial value of the servo.
        duty_min (float): Minimum duty cycle of the servo.
        duty_max (float): Maxmum duty cycle of the servo.

    Raises:
        RuntimeError: The specified pin does not exist.
        RuntimeError: The specified pin has no PWM function.
    """
    def __init__(self, pwm_pin:str, dir:float, duty_min:float, duty_max:float):
        all_pins = pinmap.get_pins()
        if pwm_pin not in all_pins:
            raise RuntimeError(f"PIN: {pwm_pin} does not exist")
        pin_functions = pinmap.get_pin_functions(pwm_pin)
        pwm_num = -1
        for pin_func in pin_functions:
            index = pin_func.find("PWM")
            if index != -1:
                pinmap.set_pin_function(pwm_pin, pin_func)
                pwm_num = int(pin_func[index+3])
                logging.debug(f"Set {pwm_pin} to function:PWM{pwm_num}")
                break
        if pwm_num == -1:
            raise RuntimeError(f"Pin {pwm_pin} doesn't have PWM function")
        self.value = dir
        self.pwm = pwm.PWM(pwm_num, 50)
        self.duty_min = duty_min
        self.duty_max = duty_max
        self.duty_range = duty_max - duty_min
        self.pwm.duty(self.value/100*self.duty_range+self.duty_min)
        self.pwm.enable()
        
    # def __del__(self):
    #     self.pwm.duty(0)
    #     self.disable()
        
    def enable(self):
        """Enable servos.
        """
        self.pwm.enable()
        
    def disable(self):
        """Disable servos.
        """
        self.pwm.disable()
        
    def dir(self, p:float):
        """Sets the servo value. 0% ~ 100%

        Args:
            p (float): value
        """
        if p > 100:
            p = 100
        elif p < 0:
            p = 0
        self.pwm.duty(p/100*self.duty_range+self.duty_min)
        
    def drive(self, inc:float):
        """Relative motion.

        Args:
            inc (float): Relative values.
        """
        self.value += inc
        if self.value > 100:
            self.value = 100
        elif self.value < 0:
            self.value = 0
        self.pwm.duty(self.value/100*self.duty_range+self.duty_min)
        
# class PID:
#     def __init__(self, kp:float, ki:float, kd:float,output_min:float, output_max:float):
#         self.kp = kp
#         self.ki = ki
#         self.kd = kd
#         self.error = 0
#         self.lerror = 0
#         self.integral = 0
#         self.output = 0
#         self.output_min = output_min
#         self.output_max = output_max
#     def calc(self, reference:float, feedback:float) -> float:
#         err = reference - feedback
#         return self.calc_err(err)
#     def calc_err(self, err:float) -> float:
#         self.lerror = self.error
#         self.error = err
#         d_out = (self.error - self.lerror) * self.kd
#         p_out = self.error * self.kp
#         self.integral += self.error * self.ki
#         self.output = p_out + d_out + self.integral
#         if self.output > self.output_max:
#             self.output = self.output_max
#         elif self.output < self.output_min:
#             self.output = self.output_min
#         return self.output 
    
class PID:
    """PID class

    Args:
        p (float, optional): kp. Defaults to 0.
        i (float, optional): ki. Defaults to 0.
        d (float, optional): kd. Defaults to 0.
        imax (float, optional): integrator_max. Defaults to 0.
    """
    _kp = _ki = _kd = _integrator = _imax = 0
    _last_error = _last_t = 0
    _RC = 1/(2 * pi * 20)
    def __init__(self, p:float=0, i:float=0, d:float=0, imax:float=0):    
        self._kp = p
        self._ki = i
        self._kd = d
        self._imax = abs(imax)
        self._last_derivative = None

    def get_pid(self, error:float, scaler:float):
        """PID calculation function.

        Args:
            error (float): Error value.
            scaler (float): Scaling factor.

        Returns:
            float: PID output.
        """
        tnow = time.time_ms()
        dt = tnow - self._last_t
        output = 0
        if self._last_t == 0 or dt > 1000:
            dt = 0
            self.reset_I()
        self._last_t = tnow
        delta_time = float(dt) / float(1000)
        output += error * self._kp
        if abs(self._kd) > 0 and dt > 0:
            if self._last_derivative == None:
                derivative = 0
                self._last_derivative = 0
            else:
                derivative = (error - self._last_error) / delta_time
            derivative = self._last_derivative + \
                                     ((delta_time / (self._RC + delta_time)) * \
                                        (derivative - self._last_derivative))
            self._last_error = error
            self._last_derivative = derivative
            output += self._kd * derivative
        output *= scaler
        if abs(self._ki) > 0 and dt > 0:
            self._integrator += (error * self._ki) * scaler * delta_time
            if self._integrator < -self._imax: self._integrator = -self._imax
            elif self._integrator > self._imax: self._integrator = self._imax
            output += self._integrator
        return output
    
    def reset_I(self):
        """Reset integrator.
        """
        self._integrator = 0
        self._last_derivative = None
    
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
    def __init__(self,  pitch:Servos, pid_pitch:PID, 
                        roll:None|Servos=None, pid_roll:None|PID=None, 
                        yaw:None|Servos=None, pid_yaw:None|PID=None):
        self._pitch = pitch
        self._roll = roll
        self._yaw = yaw
        self._pid_pitch = pid_pitch
        self._pid_roll = pid_roll
        self._pid_yaw = pid_yaw

    def run(self, pitch_err:float, roll_err:float=50, yaw_err:float=50, 
            pitch_reverse:bool=False, roll_reverse:bool=False, yaw_reverse:bool=False):
        """Perform the Gimbal operation.

        Args:
            pitch_err (float): Pitch error.
            roll_err (float, optional): Roll error. Defaults to 50.
            yaw_err (float, optional): Yaw error. Defaults to 50.
            pitch_reverse (bool, optional): Pitch reverse. Defaults to False.
            roll_reverse (bool, optional): Roll reverse. Defaults to False.
            yaw_reverse (bool, optional): Yaw reverse. Defaults to False.
        """
        out = self._pid_pitch.get_pid(pitch_err, 1)
        logging.debug(f"pitch err:{round(pitch_err, 2)}, pid_out:{round(out,2)}")
        if pitch_reverse:
            out = - out
        self._pitch.drive(out)
        if self._roll:
            out = self._pid_roll.get_pid(roll_err, 1)
            logging.debug(f"roll_err:{round(roll_err,2)}, pid_out:{round(out,2)}")
            if roll_reverse:
                out = - out
            self._roll.drive(out)
        if self._yaw:
            out = self._pid_yaw.get_pid(yaw_err, 1)
            logging.debug(f"yaw_err:{yaw_err}, pid_out:{out}")
            if yaw_reverse:
                out = - out
            self._yaw.drive(out)
            
    