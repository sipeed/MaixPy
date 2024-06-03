# Si7021 driver and get temperature and humidity
# use i2c bus to communicate with Si7021
# author: Neucrack

from maix import i2c, pinmap
import time
import sys

SI7021_ADDRESS = 0x40

class Si7021:
    SI7021_RH_READ  =             0xE5
    SI7021_TEMP_READ  =           0xE3
    SI7021_RH_READ_NO_HOLD  =     0xF5
    SI7021_TEMP_READ_NO_HOLD  =   0xF3
    SI7021_POST_RH_TEMP_READ  =   0xE0
    SI7021_RESET  =               0xFE
    SI7021_USER1_READ  =          0xE7
    SI7021_USER1_WRITE  =         0xE6

    def __init__(self, bus, address):
        self.bus = bus
        self.address = address
        self.temp = 0
        self.hum = 0
        self.test_sensor()

    def __del__(self):
        pass

    def test_sensor(self):
        slaves = self.bus.scan(self.address)
        if SI7021_ADDRESS not in slaves:
            raise Exception("No Si7021 found, please check hardware connection")

    def get_temperature(self):
        self.bus.writeto(self.address, bytes([self.SI7021_TEMP_READ]))
        self.temp = self.bus.readfrom(self.address, 1)[0]
        self.temp = self.temp << 8
        self.temp = self.temp | self.bus.readfrom(self.address, 1)[0]
        self.temp = (175.72 * self.temp / 65536) - 46.85
        return self.temp

    def get_humidity(self):
        self.bus.writeto(self.address, bytes([self.SI7021_RH_READ]))
        self.hum = self.bus.readfrom(self.address, 1)[0]
        self.hum = self.hum << 8
        self.hum = self.hum | self.bus.readfrom(self.address, 1)[0]
        self.hum = (125 * self.hum / 65536) - 6
        return self.hum


if __name__ == '__main__':
    # set pin function as i2c
    pinmap.set_pin_function("A15", "I2C5_SCL")
    pinmap.set_pin_function("A27", "I2C5_SDA")
    bus = i2c.I2C(5, i2c.Mode.MASTER)

    si = Si7021(bus, SI7021_ADDRESS)
    while 1:
        print('Temperature: %.2f C' % si.get_temperature())
        print('Humidity: %.2f %%' % si.get_humidity())
        time.sleep(1)

