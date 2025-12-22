import serial
import time
from math import pi
import logging
from src.uart_servo import UartServoManager
from src.data_table import *
from maix import uart, pinmap

logging.basicConfig(level=logging.INFO)

class Servos:
    def __init__(self, id_list:list, device_name:str, baudrate:int, min_position_list:list, max_position_list:list):
        # self.uart = serial.Serial(port=device_name, baudrate=baudrate,\
		# 			 parity=serial.PARITY_NONE, stopbits=1,\
		# 			 bytesize=8,timeout=0)
        pinmap.set_pin_function("A21", "UART4_TX")
        pinmap.set_pin_function("A22", "UART4_RX")
        self.uart = uart.UART(device_name, baudrate)
        self.uservo = UartServoManager(self.uart, servo_id_list=id_list)
        self.id_list = id_list
        for idx, id in enumerate(id_list):
            self.uservo.torque_enable(id, True)
            self.uservo.set_position(id, 2048, True)
            # self.uservo.set_lower_angle(id, min_position_list[idx])
            # self.uservo.set_upper_angle(id, max_position_list[idx])

        self.max_position_list = max_position_list
        self.min_position_list = min_position_list
        if len(self.id_list) != len(self.max_position_list) != len(self.min_position_list):
            raise RuntimeError('The lengths of id_list, max_position_list, and min_position_list must be consistent.')
        self.pitch_id = id_list[0] if len(id_list) > 0 else -1
        self.roll_id = id_list[1] if len(id_list) > 1 else -1
        self.yaw_id = id_list[2] if len(id_list) > 2 else -1
        self.value_per_angle = 4096 / 270
        
    def set_pitch(self, inc:float):
        if inc == 0:
            return
        if self.pitch_id > 0:
            curr_position = self.uservo.get_position(self.pitch_id)
            # position = curr_position + (self.value_per_angle * inc)
            position = curr_position + inc
            position = position if position >= self.min_position_list[0] else self.min_position_list[0]
            position = position if position <= self.max_position_list[0] else self.max_position_list[0]
            self.uservo.set_position(self.pitch_id, position)
            # print(f'set pitch inc:{inc:.2f}', f'position:{position:.2f}', f'range:[{self.min_position_list[0]},{self.max_position_list[0]}]')

    def set_roll(self, inc:float):
        if inc == 0:
            return
        if self.roll_id > 0:
            curr_position = self.uservo.get_position(self.roll_id)
            # position = curr_position + (self.value_per_angle * inc)
            position = curr_position + inc
            position = position if position >= self.min_position_list[1] else self.min_position_list[1]
            position = position if position <= self.max_position_list[1] else self.max_position_list[1]
            self.uservo.set_position(self.roll_id, position)
            # print(f'set roll inc:{inc:.2f}', f'position:{position:.2f}', f'range:[{self.min_position_list[1]},{self.max_position_list[1]}]')

    def set_yaw(self, inc:float):
        if inc == 0:
            return
        if self.yaw_id > 0:
            curr_position = self.uservo.get_position(self.yaw_id)
            position = curr_position + (self.value_per_angle * inc)
            self.uservo.set_position(self.yaw_id, position)
 
    def test_position(self):
        for id in self.id_list:
            self.uservo.torque_enable(id, False)
        
        while True:
            for id in self.id_list:
                print(f'id:{id} position:{self.uservo.get_position(id)}')
            time.sleep(1)

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
        tnow = time.time() * 1000
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
        servos (Servos): Servos.
        pid_pitch (PID): Pitch PID.
        pid_roll (None | PID, optional): Roll PID. Defaults to None.
        pid_yaw (None | PID, optional): Yaw PID. Defaults to None.
    """
    def __init__(self,  servos:Servos, pid_pitch:PID, pid_roll:None|PID=None, pid_yaw:None|PID=None):
        self._servos = servos
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
        self._servos.set_pitch(out)
        if self._pid_roll:
            out = self._pid_roll.get_pid(roll_err, 1)
            logging.debug(f"roll_err:{round(roll_err,2)}, pid_out:{round(out,2)}")
            if roll_reverse:
                out = - out
            self._servos.set_roll(out)
        if self._pid_yaw:
            out = self._pid_yaw.get_pid(yaw_err, 1)
            logging.debug(f"yaw_err:{yaw_err}, pid_out:{out}")
            if yaw_reverse:
                out = - out
            self._servos.set_yaw(out)
            
    