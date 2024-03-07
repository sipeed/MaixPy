
from maix.peripheral import uart

class UART:
    UART1 = 1
    UART2 = 2
    UART3 = 3
    UART4 = 4
    PARITY_NONE = 0
    PARITY_ODD = 1
    PARITY_EVEN = 2

    def __init__(self, device, baudrate, bits = 8, parity = None, stop = 1, timeout=1000, read_buf_len=4096):
        if device == UART.UART1:
            device = "/dev/ttyS0"
        elif device == UART.UART2:
            device = "/dev/ttyS1"
        elif device == UART.UART3:
            device = "/dev/ttyS2"
        elif device == UART.UART4:
            device = "/dev/ttyS3"
        elif type(device) == str:
            pass
        else:
            raise Exception("Invalid device")
        self.device = device
        self.timeout = timeout
        self.init(baudrate, bits, parity, stop, timeout, read_buf_len)

    def read(self, num=-1):
        return self._uart.read()

    def readline(self):
        return self._uart.readline(timeout = self.timeout)

    def write(self, data):
        return self._uart.write(data)

    def any(self):
        return self._uart.available()

    def init(self, baudrate, bits = 8, parity = None, stop = 1, timeout=1000, read_buf_len=4096):
        if bits == 5:
            bits = uart.BITS.BITS_5
        elif bits == 6:
            bits = uart.BITS.BITS_6
        elif bits == 7:
            bits = uart.BITS.BITS_7
        elif bits == 8:
            bits = uart.BITS.BITS_8
        else:
            raise Exception("Invalid bits")
        if parity is None:
            parity = uart.PARITY.PARITY_NONE
        elif parity == UART.PARITY_ODD:
            parity = uart.PARITY.PARITY_ODD
        elif parity == UART.PARITY_EVEN:
            parity = uart.PARITY.PARITY_EVEN
        else:
            raise Exception("Invalid parity")
        if stop == 1:
            stop = uart.STOP.STOP_1
        elif stop == 2:
            stop = uart.STOP.STOP_2
        elif stop == 1.5:
            stop = uart.STOP.STOP_1_5
        else:
            raise Exception("Invalid stop")
        self._uart = uart.UART(self.device, baudrate, bits, parity, stop)
        self.timeout = timeout

    def deinit(self):
        self._uart.close()
