---
title: Using Modbus Protocol with MaixCAM MaixPy
---

MaixPy has adapted the Modbus protocol, with its underlying implementation based on [libmodbus](https://libmodbus.org/).

Using the Modbus protocol on MaixPy is straightforward. Here’s what you need to know:

* When you use `modbus.Slave`, MaixCAM(Pro) acts as a slave device (such as a sensor module), and the controlling device is the master (such as your MCU/PC). The master can read and write registers from the slave device just like reading and writing chip registers.

* You can think of it simply as:

    > From the master's perspective, `coils` are read/write register groups storing a set of boolean values; `discrete input` are read-only register groups storing a set of boolean values; `input registers` are read-only register groups storing a set of 16-bit int values; `holding registers` are read/write register groups storing a set of 16-bit int values.

    > From the slave's perspective, all register groups are read/write and can be custom-sized. The other characteristics are consistent with the master's view.

Example:

```python
from maix.comm import modbus
from maix import app, err

slave = modbus.Slave(
    modbus.Mode.RTU,    # Modbus mode set to RTU
    "/dev/ttyS0",       # Serial port for communication with the master
    0x00, 10,           # Start address and number of coils
    0x00, 10,           # Start address and number of discrete inputs
    0x00, 10,           # Start address and number of input registers
    0x00, 10,           # Start address and number of holding registers
    115200, 1,          # Baud rate 115200, default 8N1, the last 1 represents the RTU slave address
    0, False            # TCP port number (irrelevant for RTU), the latter is whether to print debug information
)

"""
Taking the coils register group as an example, the start address is 0x00, and the number is 10, which means the address range of the slave's coils register group is 0x00~0x09, with a total of 10 registers, each storing a boolean value.
"""

# Read all values from the current input registers group
# Initial values in the registers are all 0
old_ir = slave.input_registers()
print("old ir: ", old_ir)

# Update the values in the input registers starting from index 2
# The register group values will become [0x00 0x00 0x22 0x33 0x44 0x00 0x00 0x00 0x00 0x00]
data : list[int] = [0x22, 0x33, 0x44]
slave.input_registers(data, 2)
# Read and print to verify
new_ir = slave.input_registers()
print("new ir:", new_ir)


while not app.need_exit():
    # Wait for the master's read/write operation
    if err.Err.ERR_NONE != slave.receive(2000): #timeout 2000ms
        continue

    # Get the master's operation type
    rtype = slave.request_type()
    # If the master wants to read holding registers
    if rtype == modbus.RequestType.READ_HOLDING_REGISTERS:
        # Prepare data
        # Get and view the current holding registers data
        print("master read hr")
        hr = slave.holding_registers()
        print("now hr: ", hr)

        # Update all data in holding registers
        hr = [x+1 for x in hr]
        print("now we make hr+1: ", hr)
        print("update hr")
        slave.holding_registers(hr)
    # else ... handle other operations

    # Automatically handle the master's request, automatically update register values
    slave.reply()
```

```python
from maix.comm import modbus
from maix import app, err

slave = modbus.Slave(
    modbus.Mode.TCP,    # Mode: TCP
    "",                 # Keep empty
    0x00, 10,
    0x00, 10,
    0x00, 10,
    0x00, 10,
    0, 1,               # We are using TCP mode, ignore baud rate and RTU address
    5020, False         # TCP port number, the latter is whether to print debug information
)

### The following code is consistent with the RTU part

old_ir = slave.input_registers()
print("old ir: ", old_ir)
data : list[int] = [0x22, 0x33, 0x44]
slave.input_registers(data, 3)
new_ir = slave.input_registers()
print("new ir:", new_ir)

while not app.need_exit():
    if err.Err.ERR_NONE != slave.receive(2000): #timeout 2000ms
        continue

    rtype = slave.request_type()
    if rtype == modbus.RequestType.READ_HOLDING_REGISTERS:
        print("master read hr")
        hr = slave.holding_registers()
        print("now hr: ", hr)
        hr = [x+1 for x in hr]
        print("now we make hr+1: ", hr)
        print("update hr")
        slave.holding_registers(hr)

    slave.reply()
```

This way, we can use MaixCAM(Pro) as a slave device, and the master can read (write) its registers at any time.

For detailed Modbus API documentation, please refer to the [Modbus API Documentation](../../../api/maix/comm/modbus.md).