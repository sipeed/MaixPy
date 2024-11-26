---
title: MaixCAM MaixPy Using Modbus Protocol
---

## Introduction to Modbus

Modbus is an application-layer bus protocol that operates over UART or TCP as the transport layer.  
It allows multiple devices to connect to a single bus, enabling one-to-many communication.

## Differences Between Modbus and Maix Application Communication Protocol

* **Maix Application Communication Protocol**:
  * **Communication Type**: One-to-one communication.
  * **Communication Mode**: Full-duplex, allowing both parties to actively send messages for more real-time interaction.
  * **Data Flexibility**: No restrictions on data length or type, supporting flexible data structures.
  * **MaixCAM MaixPy integrated**: By default some MaixCAM/MaixPy APP impleted this protocol, you can directly use it, and use same protocol is good for MaixCAM/MaixPy ecosystem health.
  * **Application Scenarios**: Suitable for one-to-one scenarios requiring high real-time performance and bidirectional data transmission, such as AI inference result transmission and control command feedback. And communicate with MaixCAM MaixPy's applications.

* **Modbus**:
  * **Communication Type**: A bus protocol supporting one-to-many communication.
  * **Communication Mode**: Only the master can initiate read/write operations. The slave's data updates are obtained by the master's polling mechanism, and slaves can essentially be regarded as sensors with multiple groups of registers.
  * **Data Type**: Data is organized into registers. Slaves have multiple readable/writable or read-only registers for data exchange.
  * **Application Scenarios**: Suitable for industrial automation scenarios where data collection and monitoring of sensors or devices are needed, especially in master-slave structured systems.

## Using Modbus with MaixCAM MaixPy

MaixPy supports the Modbus protocol, including both master and slave modes, as well as RTU (UART) and TCP modes.  
The implementation is based on the open-source project [libmodbus](https://libmodbus.org/).

## MaixCAM as a Modbus Slave

When acting as a slave, MaixCAM can be seen as a module with several groups of readable/writable registers.

The registers include the following types, which differ in value type and read/write permissions:
* **`coils` Registers**: Boolean values, readable and writable.
* **`discrete input` Registers**: Boolean values, readable but not writable.
* **`input registers`**: 16-bit integer values, readable but not writable.
* **`holding registers`**: 16-bit integer values, readable and writable.

The address and length of each register group can be freely specified during slave initialization based on application requirements.

Below are examples. For more code, refer to the source examples (`examples/protocol/comm_modbus_xxx.py`).

### RTU (UART):

```python
from maix.comm import modbus
from maix import app, err

slave = modbus.Slave(
    modbus.Mode.RTU,    # Set Modbus mode to RTU
    "/dev/ttyS0",       # Specify the UART port for communication with the master
    0x00, 10,           # Start address and number of registers for coils
    0x00, 10,           # Start address and number of registers for discrete input
    0x00, 10,           # Start address and number of registers for input registers
    0x00, 10,           # Start address and number of registers for holding registers
    115200, 1,          # Baud rate of 115200, default 8N1; the last `1` is the slave address for RTU
    0, False            # TCP port (irrelevant for RTU), debug flag
)

"""
Example: Coils register group
Start address: 0x00
Number: 10
This means the coils register group ranges from 0x00 to 0x09, with each register storing a Boolean value.
"""

# Read all values from the input registers group
old_ir = slave.input_registers()
print("Old input registers:", old_ir)

# Update values in the input registers group starting from index 2
# New register values: [0x00, 0x00, 0x22, 0x33, 0x44, 0x00, 0x00, 0x00, 0x00, 0x00]
data: list[int] = [0x22, 0x33, 0x44]
slave.input_registers(data, 2)

# Read and verify updated values
new_ir = slave.input_registers()
print("New input registers:", new_ir)

while not app.need_exit():
    # Wait for the master's read/write operation
    if err.Err.ERR_NONE != slave.receive(2000):  # Timeout: 2000ms
        continue

    # Determine the type of operation requested by the master
    rtype = slave.request_type()
    if rtype == modbus.RequestType.READ_HOLDING_REGISTERS:
        print("Master requested to read holding registers")
        hr = slave.holding_registers()
        print("Current holding registers:", hr)

        # Update holding registers with new values
        hr = [x + 1 for x in hr]
        slave.holding_registers(hr)

    # Automatically handle the master's request and update register values
    slave.reply()
```

### TCP:

```python
from maix.comm import modbus
from maix import app, err

slave = modbus.Slave(
    modbus.Mode.TCP,    # Set mode to TCP
    "",                 # Leave blank for TCP mode
    0x00, 10,           # Start address and number of registers for coils
    0x00, 10,           # Start address and number of registers for discrete input
    0x00, 10,           # Start address and number of registers for input registers
    0x00, 10,           # Start address and number of registers for holding registers
    0, 1,               # TCP port; the last parameter is the debug flag
)

# The following code is identical to the RTU example

old_ir = slave.input_registers()
print("Old input registers:", old_ir)

data: list[int] = [0x22, 0x33, 0x44]
slave.input_registers(data, 2)
new_ir = slave.input_registers()
print("New input registers:", new_ir)

while not app.need_exit():
    if err.Err.ERR_NONE != slave.receive(2000):  # Timeout: 2000ms
        continue

    rtype = slave.request_type()
    if rtype == modbus.RequestType.READ_HOLDING_REGISTERS:
        print("Master requested to read holding registers")
        hr = slave.holding_registers()
        print("Current holding registers:", hr)

        hr = [x + 1 for x in hr]
        print("Updated holding registers:", hr)
        slave.holding_registers(hr)

    slave.reply()
```

As shown above, calling `slave.reply()` after receiving a read request from the master automatically replies with the requested data. The example also demonstrates how to modify the register values on the slave side.

For detailed information on the Modbus API, refer to the [Modbus API Documentation](../../../api/maix/comm/modbus.md).


## MaixCAM MaixPy as Modbus Master

As a master, MaixCAM can actively read and write data from/to slaves. Below is an example (refer to the source example `examples/protocol/comm_modbus_xxx.py` for more details):

```python
from maix import pinmap, app, err, time, thread
from maix.comm import modbus

REGISTERS_START_ADDRESS = 0x00  # Start address for registers
REGISTERS_NUMBER = 10           # Number of registers to read

RTU_SLAVE_ID = 1                # Slave ID
RTU_BAUDRATE = 115200           # Baud rate for UART communication

def master_thread(*args):
    # Initialize UART1 for Modbus communication
    if pinmap.set_pin_function("A19", "UART1_TX") != err.Err.ERR_NONE:
        print("Failed to initialize UART1 TX!")
        exit(-1)
    if pinmap.set_pin_function("A18", "UART1_RX") != err.Err.ERR_NONE:
        print("Failed to initialize UART1 RX!")
        exit(-1)

    # Optional: Enable debugging for Modbus master
    # modbus.set_master_debug(True)

    # Create a Modbus master instance with RTU mode
    master = modbus.MasterRTU(
        "/dev/ttyS1",    # UART device for communication
        RTU_BAUDRATE     # Baud rate
    )

    while not app.need_exit():
        # Read holding registers from the slave
        hr = master.read_holding_registers(
            RTU_SLAVE_ID,              # Slave ID
            REGISTERS_START_ADDRESS,   # Starting address of registers
            REGISTERS_NUMBER,          # Number of registers to read
            2000                       # Timeout in milliseconds
        )
        
        # Check if the read operation was successful
        if len(hr) == 0:
            continue

        # Print the read data
        print("Master read holding registers:", hr)

        # Wait for 1 second before the next read
        time.sleep(1)

# Start the master thread
master_thread(None)
```

This example demonstrates using UART1 as the master to read register values from a slave device.

