from maix import time, app
from maix.ext_dev import axp2101

axp = axp2101.AXP2101()

# Get battery percent
print(f"Battery percent: {axp.get_bat_percent()}%")

# Set the max battery charging current
charging_current = axp2101.ChargerCurrent.CHG_CUR_1000MA
axp.set_bat_charging_cur(charging_current)
max_charging_current = (int(axp.get_bat_charging_cur()) - 8) * 100 + 200
print(f"Max charging current: {max_charging_current}mA")

# Set DCDC1 voltage (!!! Do not modify the voltage of other channels,
# as it may damage the device.)
old_dcdc1_voltage = axp.dcdc1()
new_dcdc1_voltage = axp.dcdc1(3000)
print(f"Old DCDC1 voltage: {old_dcdc1_voltage}mV")
print(f"New DCDC1 voltage: {new_dcdc1_voltage}mV")

# List all power channels for voltage reading
channels = [
    ('DCDC1', axp.dcdc1),
    ('DCDC2', axp.dcdc2),
    ('DCDC3', axp.dcdc3),
    ('DCDC4', axp.dcdc4),
    ('DCDC5', axp.dcdc5),
    ('ALDO1', axp.aldo1),
    ('ALDO2', axp.aldo2),
    ('ALDO3', axp.aldo3),
    ('ALDO4', axp.aldo4),
    ('BLDO1', axp.bldo1),
    ('BLDO2', axp.bldo2),
]

# Get all channel voltages
print("------ All channel voltage: ------")
for name, channel in channels:
    print(f"{name}: {channel()}")
print("----------------------------------")

# Set power-off time, device will shut down if the 
# power button is held down longer than this time.
axp.set_poweroff_time(axp2101.PowerOffTime.POWEROFF_4S)

# Set power-on time, device will power on if the 
# power button is held down longer than this time.
axp.set_poweron_time(axp2101.PowerOnTime.POWERON_128MS)

# Poweroff (Important! Power will be cut off immediately)
# axp.poweroff()

while not app.need_exit():
    time.sleep_ms(1000)