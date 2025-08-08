---
title: MaixCAM MaixPy ADC 使用介绍
update:
  - date: 2024-06-11
    author: iawak9lkm
    version: 1.0.0
    content: 初版文档
---

## 支持的设备

| 设备      | 是否支持 |
| -------- | ------- |
| MaixCAM2 | ❌ |
| MaixCAM / MaixCAM-Pro  | ✅ |


## ADC 简介

ADC，即模拟信号数字转换器，将一个输入电压信号转换为一个输出的数字信号。由于数字信号本身不具有实际意义，仅仅表示一个相对大小。故任何一个模数转换器都需要一个参考模拟量作为转换的标准，参考标准一般为最大的可转换信号大小。而输出的数字量则表示输入信号相对于参考信号的大小。

ADC 外设一般有两个主要参数：分辨率和参考电压。

* 分辨率：ADC 的分辨率以输出二进制（或十进制）数的位数来表示。它说明 A/D 转换器对输入信号的分辨能力。一般来说，n 位输出的 A/D 转换器能区分 2^n 个不同等级的输入模拟电压，能区分输入电压的最小值为满量程输入的 1/(2^n)。在最大输入电压一定时，输出位数愈多，分辨率愈高。
* 参考电压：ADC 参考电压是在 AD 转换过程中与已知电压进行比较来找到未知电压的值的电压。参考电压可以认为是最高上限电压，当信号电压较低时，可以降低参考电压来提高分辨率。

通过板子的 ADC，可以采集外部的电压，并让板子检验电压是否达标，或是在检测到特定的电压时执行特定的任务（例如 ADC 检测多个按钮）。

## MaixPy 中使用 ADC

通过 MaixPy 使用 ADC 很简单：

```python
from maix.peripheral import adc
from maix import time

a = adc.ADC(0, adc.RES_BIT_12)

raw_data = a.read()
print(f"ADC raw data:{raw_data}")

time.sleep_ms(50)

vol = a.read_vol()
print(f"ADC vol:{vol}")
```

使用 ADC0，从中读取原始的转换数据，或是直接从中读取电压数据。

有关 ADC API 的详细说明请看 [ADC API 文档](../../../api/maix/peripheral/adc.md)

## 关于 MaixCAM ADC 外设的一些说明

MaixCAM 引出一个连接 ADC 的 IO，为 GPIO B3，如下图所示（对于MaixCAM-Pro 由于 B3 已经连接到了闪光灯， ADC 无法直接使用）：

![](https://wiki.sipeed.com/hardware/zh/lichee/assets/RV_Nano/intro/RV_Nano_3.jpg)

该 IO 默认为 ADC， 无需额外进行配置。

MaixCAM ADC 外设采样精度为 12bit，也就是说采样输出范围为 0~4095。采样精度为参考电压的 1/4096。

MaixCAM ADC 外设的扫描频率不能高于 320K/s，也就是上述示例中增加延时的原因。

MaixCAM ADC 外设内部参考电压Vref为 1.5V，实际使用时会有些许偏差。因为内部参考电压典型值为 1.5V，所以 Soc 的 ADC 量程为 0～1.5V。该量程的 ADC 应用范围较小，故 MaixCAM 额外为 ADC 外设设计了分压电路来增大 ADC 的应用范围，该分压电路如下图所示。由于电路中电阻阻值存在误差、ADC 外设有阻抗、内部参考电压有些许偏差，该分压电路的参考电压 Vin_max 约为 4.6~5.0V。API 中已经选择一个精度较高的默认值，一般情况下无需传递该参数。

![](https://wiki.sipeed.com/hardware/zh/lichee/assets/RV_Nano/peripheral/adc.png)

若需要较高的精度，可以通过以下步骤计算出该分压电路的参考电压：

* 先测得 ADC_PIN 的实际输入电压 Vin。

* 然后测得 ADC1 处的实际输入电压 Vadc，电阻R10的位置可参考这个 [BOM](https://cn.dl.sipeed.com/fileList/LICHEE/LicheeRV_Nano/03_Designator_drawing/LicheeRV_Nano-70405_iBOM.rar) 表。

* 保持第一步的电压输入，在shell中执行以下命令：

  ```shell
  echo 1 > /sys/class/cvi-saradc/cvi-saradc0/device/cv_saradc
  cat /sys/class/cvi-saradc/cvi-saradc0/device/cv_saradc
  ```

  此时你将获得 ADC 原始数据 adc_data。

* 接地电阻为 R10，另一个电阻为 R6, 记录它们的阻值。通常，MaixCAM 的 R6 阻值为 10KΩ（10 000Ω），R10  阻值为 5.1KΩ（5 100Ω）。

* 将上述参数传递给以下 python 代码，即可得出 ADC_PIN 端的量程 [0, Vin_max] （闭区间）。

  ```python
  def maixcam_get_vin_max(Vin:float, Vadc:float, adc_data:int, r6:int, r10:int, adc_max:int=4095):
      Vref = (Vadc/adc_data)*(adc_max+1)
      r3 = Vadc*r6/(Vin-Vadc)
      Vin_max = (Vref/r3)*(r6+r3)
      return Vin_max
  
  Vin = 3.3		# step 1
  Vadc = 1.06		# step 2
  adc_data=2700	# step 3
  r6=10000		# step 4
  r10=5100		# step 4
  
  if __name__ == '__main__':
      print(maixcam_get_vin_max(Vin, Vadc, adc_data, r6, r10))
  ```

  现在将结果传递给 `adc.ADC()` 的第三个参数，你将获得一个高精度的 ADC。

