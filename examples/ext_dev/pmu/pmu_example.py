from maix import time, app
from maix.ext_dev import pmu

p = pmu.PMU("axp2101")

# Get battery percent
print(f"Battery percent: {p.get_bat_percent()}%")

# Set the max battery charging current
p.set_bat_charging_cur(1000)
print(f"Max charging current: {p.get_bat_charging_cur()}mA")

# Set DCDC1 voltage (!!! Do not modify the voltage of other channels,
# as it may damage the device.)
old_dcdc1_voltage = p.get_vol(pmu.PowerChannel.DCDC1)
print(f"Old DCDC1 voltage: {old_dcdc1_voltage}mV")
p.set_vol(pmu.PowerChannel.DCDC1, 3000)
new_dcdc1_voltage = p.get_vol(pmu.PowerChannel.DCDC1)
print(f"New DCDC1 voltage: {new_dcdc1_voltage}mV")

# Get all channel voltages
channels = [
    pmu.PowerChannel.DCDC1, pmu.PowerChannel.DCDC2, pmu.PowerChannel.DCDC3,
    pmu.PowerChannel.DCDC4, pmu.PowerChannel.DCDC5, pmu.PowerChannel.ALDO1,
    pmu.PowerChannel.ALDO2, pmu.PowerChannel.ALDO3, pmu.PowerChannel.ALDO4,
    pmu.PowerChannel.BLDO1, pmu.PowerChannel.BLDO2
]

print("------ All channel voltages: ------")
for channel in channels:
    print(f"{channel.name}: {p.get_vol(channel)}")
print("-----------------------------------")

# Poweroff (Important! Power will be cut off immediately)
# p.poweroff()

while not app.need_exit():
    time.sleep_ms(1000)