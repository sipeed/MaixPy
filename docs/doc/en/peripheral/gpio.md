# MaixCAM MaixPy Using GPIO

## Introduction

Using GPIO allows you to control pins for input or output high and low levels, which is commonly used to read signals or output control signals.

**Note:** The pins on the `MaixCAM` are tolerant to `3.3V`. Do not input `5V` voltage.

## Using GPIO in MaixPy

> MaixPy Firmware should > 4.1.2(not include)

First, we need to know which pins and GPIOs the device has. For MaixCAM, each pin corresponds to a GPIO controller, as shown in the figure:

![](https://wiki.sipeed.com/hardware/zh/lichee/assets/RV_Nano/intro/RV_Nano_3.jpg)
![maixcam_pro_io](/static/image/maixcam_pro_io.png)

It is important to note that pins can be used not only as GPIOs but also for other functions like PWM. Before using them, we need to set the pin function to GPIO.

For example, on MaixCAM, **some pins are already occupied by other functions by default, such as UART0 and WiFi (SDIO1 + A26), so it is not recommended to use them.**

Other pins can be used, and the A14 pin is connected to the onboard LED, which is used as a system load indicator by default. If initialized, it will automatically disable the system indicator function and can be used as a regular GPIO (note that `A14` can only be used as an output). This way, you can control the LED's on and off state.

Here is the English translation of your text:

The circuit diagram of the LED is shown in the figure. Therefore, we only need to provide a high signal to pin A14, and the LED will conduct and light up:
![](../../assets/gpio_led.png)

```python
from maix import gpio, pinmap, time

pinmap.set_pin_function("A14", "GPIOA14")
led = gpio.GPIO("GPIOA14", gpio.Mode.OUT)
led.value(0)

while 1:
    led.toggle()
    time.sleep_ms(500)
```

Here, we first use `pinmap` to set the function of the `A14` pin to `GPIO`. Of course, for `A14`, since it only has the `GPIO` function, it can be omitted. For the sake of generality, other pins may need to be set, so it is set in this example.

For more APIs, please refer to the [GPIO API Documentation](https://wiki.sipeed.com/maixpy/api/maix/peripheral/gpio.html)

## GPIO in Input Mode

```python
from maix import gpio, pinmap, time

pinmap.set_pin_function("A19", "GPIOA19")
led = gpio.GPIO("GPIOA19", gpio.Mode.IN)

while 1:
    print(led.value())
    time.sleep_ms(1) # sleep to make cpu free
```

Here is the English translation of the text:

## MaixCAM-Pro Uses Illumination LED

Both MaixCAM and MaixCAM-Pro have a small LED light connected to pin `A14`. Additionally, the MaixCAM-Pro has an onboard illumination LED connected to pin `B3`, which is turned on by a high signal and off by a low signal:

```python
from maix import gpio, pinmap, time

pinmap.set_pin_function("B3", "GPIOB3")
led = gpio.GPIO("GPIOB3", gpio.Mode.OUT)
led.value(0)

while 1:
    led.toggle()
    time.sleep_ms(500)

```


