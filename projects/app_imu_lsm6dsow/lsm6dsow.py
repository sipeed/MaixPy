import smbus2
import struct
import numpy as np

class Lsm6dsow:
    STATUS_REG = 0x1E
    ACC_REG = 0x28
    GYRO_REG = 0x22
    CTRL1_XL = 0x10  # Accelerometer ODR/scale
    CTRL2_G = 0x11   # Gyro ODR/scale

    ACC_SENS_TABLE = {0:0.061, 1:0.122, 2:0.244, 3:0.488}
    GYRO_SENS_TABLE = {0:8.75, 1:17.5, 2:35, 3:70}
    GRAVITY = 9.80665
    ODR_TABLE = [0, 12.5, 26, 52, 104, 208, 416, 833, 1660, 3330, 6660]

    def __init__(self, i2c_bus=1, dev_addr=0x6b):
        self.bus = smbus2.SMBus(i2c_bus)
        self.addr = dev_addr
        self._last_frame = np.zeros((2,3))  # [acc, gyro] last valid
        self._last_updated = 0

    def _read_reg(self, reg, length=1):
        if length == 1:
            return self.bus.read_byte_data(self.addr, reg)
        return self.bus.read_i2c_block_data(self.addr, reg, length)

    def _write_reg(self, reg, value):
        self.bus.write_byte_data(self.addr, reg, value)

    def get_acc_odr(self):
        val = self._read_reg(self.CTRL1_XL)
        odr_idx = (val >> 4) & 0x0F
        return self.ODR_TABLE[odr_idx] if odr_idx < len(self.ODR_TABLE) else 0

    def set_acc_odr(self, hz):
        idx = min(range(len(self.ODR_TABLE)), key=lambda i: abs(self.ODR_TABLE[i]-hz))
        val = self._read_reg(self.CTRL1_XL)
        val = (val & 0x0F) | (idx << 4)
        self._write_reg(self.CTRL1_XL, val)

    def get_gyro_odr(self):
        val = self._read_reg(self.CTRL2_G)
        odr_idx = (val >> 4) & 0x0F
        return self.ODR_TABLE[odr_idx] if odr_idx < len(self.ODR_TABLE) else 0

    def set_gyro_odr(self, hz):
        idx = min(range(len(self.ODR_TABLE)), key=lambda i: abs(self.ODR_TABLE[i]-hz))
        val = self._read_reg(self.CTRL2_G)
        val = (val & 0x0F) | (idx << 4)
        self._write_reg(self.CTRL2_G, val)

    def get_acc_scale(self):
        val = self._read_reg(self.CTRL1_XL)
        fs = (val >> 2) & 0x03
        return self.ACC_SENS_TABLE.get(fs, 0.061)

    def set_acc_scale(self, g_val):
        fs_map = {2:0, 4:1, 8:2, 16:3}
        fs = fs_map.get(g_val, 0)
        val = self._read_reg(self.CTRL1_XL)
        val = (val & ~(0x0C)) | (fs << 2)
        self._write_reg(self.CTRL1_XL, val)

    def get_gyro_scale(self):
        val = self._read_reg(self.CTRL2_G)
        fs = (val >> 2) & 0x03
        return self.GYRO_SENS_TABLE.get(fs, 8.75)

    def set_gyro_scale(self, dps_val):
        fs_map = {250:0, 500:1, 1000:2, 2000:3}
        fs = fs_map.get(dps_val, 0)
        val = self._read_reg(self.CTRL2_G)
        val = (val & ~(0x0C)) | (fs << 2)
        self._write_reg(self.CTRL2_G, val)

    def read(self):
        status = self._read_reg(self.STATUS_REG)
        updated = 0
        if (status & 0x01) and (status & 0x02):
            acc_bytes = self._read_reg(self.ACC_REG, 6)
            gyro_bytes = self._read_reg(self.GYRO_REG, 6)
            acc_raw = np.array(struct.unpack('<hhh', bytes(acc_bytes)), dtype=np.int16)
            gyro_raw = np.array(struct.unpack('<hhh', bytes(gyro_bytes)), dtype=np.int16)
            acc_scale = self.get_acc_scale()
            gyro_scale = self.get_gyro_scale()
            acc_val = acc_raw * acc_scale * self.GRAVITY / 1000      # m/s²
            gyro_val = gyro_raw * gyro_scale / 1000                  # °/s
            self._last_frame = np.array([acc_val, gyro_val])
            updated = 1
        else:
            # No new data, return last
            updated = 0
        return updated, self._last_frame.copy()

    def read_raw(self):
        acc_bytes = self._read_reg(self.ACC_REG, 6)
        gyro_bytes = self._read_reg(self.GYRO_REG, 6)
        acc_raw = np.array(struct.unpack('<hhh', bytes(acc_bytes)), dtype=np.int16)
        gyro_raw = np.array(struct.unpack('<hhh', bytes(gyro_bytes)), dtype=np.int16)
        return np.array([acc_raw, gyro_raw])