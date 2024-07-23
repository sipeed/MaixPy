from maix.v1.machine import UART
from maix import time


uart_A = UART("/dev/serial0", 115200)


time.sleep_ms(100) # wait uart ready
uart_A.write(b'hello world')

while True:
  if uart_A.any():
    while uart_A.any():
      read_data = uart_A.read()
      print("recv = ", read_data) # recv =  b'hello world'
    break
  time.sleep_ms(10) # other event

print("deinit")
uart_A.deinit()
del uart_A
print("exit")
