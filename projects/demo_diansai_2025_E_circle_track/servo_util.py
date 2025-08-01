"""
    Author: Neucrack
    Date: 2025-07-29
    License: MIT
"""

from maix import pwm, pinmap, time

class Servo:
    """Servo control class

    Args:
        pwm_pin (str): PWM pin to be used, e.g. “A17”.
        angle (float): Initial angle of the servo, unit is percentage of angle range, range [0, 100], not degree.
        duty_range ([float, float]): Duty cycle range of the servo, unit is percent. For most servos is 2.5% (20ms * 0.025 = 0.5ms).
        duty_max (float): Maxmum duty cycle of the servo, unit is percent. For most servos is 12.5% (20ms * 0.125 = 2.5ms).
        freq: (int, optional): PWM frequency, default is 50(Hz)(20ms).

    Raises:
        ValueError: The specified pin does not exist.
        ValueError: The specified pin has no PWM function.
    """
    def __init__(self, pwm_pin:str, angle:float, duty_range:float, freq = 50):
        all_pins = pinmap.get_pins()
        if pwm_pin not in all_pins:
            raise ValueError(f"PIN: {pwm_pin} does not exist")
        pin_functions = pinmap.get_pin_functions(pwm_pin)
        pwm_num = -1
        for pin_func in pin_functions:
            index = pin_func.find("PWM")
            if index != -1:
                pinmap.set_pin_function(pwm_pin, pin_func)
                pwm_num = int(pin_func[index+3])
                print(f"Set {pwm_pin} to function:PWM{pwm_num}")
                break
        if pwm_num == -1:
            raise ValueError(f"Pin {pwm_pin} doesn't have PWM function")
        self.angle = angle
        self.pwm = pwm.PWM(pwm_num, freq)
        self.duty_min = duty_range[0]
        self.duty_max = duty_range[1]
        self.duty_range = self.duty_max - self.duty_min
        self.set_angle(angle)
        self.enable()

    def _angle_to_duty(percent):
        return self.duty_range * percent / 100.0 + self.duty_min

    def __del__(self):
        self.pwm.duty(0)
        self.disable()

    def enable(self):
        """Enable servos.
        """
        self.pwm.enable()

    def disable(self):
        """Disable servos.
        """
        self.pwm.disable()

    def set_angle(self, percent : float):
        """Sets the servo angle percentage.

        Args:
            percent (float): angle percentage, range [0, 100].
        """
        if percent > 100:
            percent = 100
        elif percent < 0:
            percent = 0
        self.angle = percent
        self.pwm.duty(self.angle * self.duty_range / 100.0 + self.duty_min)

    def get_angle(self) -> float:
        """Get the current angle percentage.

        Returns:
            float: Current angle percentage, range [0, 100].
        """
        return self.angle


    def drive(self, inc:float):
        """Relative motion.

        Args:
            inc (float): Relative increase angle percentage value.
        """
        self.angle += inc
        if self.angle > 100:
            self.angle = 100
        elif self.angle < 0:
            self.angle = 0
        self.pwm.duty(self.angle * self.duty_range / 100.0 + self.duty_min)


