from math import pi
from maix import time

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
        tnow = time.ticks_ms()
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

