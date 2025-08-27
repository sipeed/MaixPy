---
title: MaixCAM MaixPy Using GPIO
---

## Introduction

Using GPIOs allows you to control a pin to output a high or low voltage level or to read a signal from it. This is a very common way to read signals or output control signals.

**Note:** The pins on the `MaixCAM` are `3.3V` tolerant. **Do not** apply `5V` to them.

## Prerequisites

Please learn how to use the [pinmap](https://www.google.com/search?q=./pinmap.md) module to set pin functions first.

To enable a pin for `GPIO` functionality, first use `pinmap` to set the function of the corresponding pin to `GPIO`.

## Choosing the Right GPIO to Use

First, you need to know which pins on your device are available as GPIOs, as shown in the figure:

| Device Model | Pinout Diagram | Pin Multiplexing Description |
| ------- | ------- | --- |
| MaixCAM |  | The silkscreen on the board, e.g., `A19`, is the pin name, and `GPIOA19/PWM7` is the function name |
| MaixCAM-Pro |  | The first name, e.g., `A19`, is the pin name, and `GPIOA19/PWM7` is the corresponding function name |
| MaixCAM2 |  | The first name, e.g., `A2`, is the pin name, and `GPIOA2/SPI1_CS0` is the corresponding function name, that is, just add `GPIO` prefix for IO name to use `GPIO` funtion |

Note that pins may have other default uses. It's best to avoid these pins. Please refer to the [pinmap](https://www.google.com/search?q=./pinmap.md) documentation for details.

## Circuit Considerations

Be aware that the voltage tolerance and load capacity of the pins are limited. You need to be careful when designing circuits to avoid basic mistakes, like asking "why can't the pin directly power a motor?"

  * **Pin Voltage Tolerance**: Unless otherwise specified, the pins operate at `3.3v`. Do not connect an external `5v` voltage.
  * **Pin Input/Output Current**: The input/output current of the chip pins is limited. They are generally only used for control signals. For devices with high current requirements, please use a conversion circuit.

**Example**: To control an LED, a simple circuit is as follows:
The `LED` is directly powered by a high-level output from the pin. This is the most intuitive way to use it, but you must be very careful. The maximum output and input current of a chip pin (the driving capability) is limited and is usually described in the chip's datasheet.
Here, the current is `3.3v/(LED+resistor resistance)` \< `0.64mA`, so it can be driven directly. However, if your circuit's current is too high, it may fail to drive the device or even cause the chip to malfunction.

The **correct approach** is to connect an external conversion circuit so the pin only acts as a control signal. This can be done using a transistor, optocoupler, or relay. This document won't go into details; please do your own research.

## GPIO Output Mode

As shown in the LED circuit diagram, we only need to provide a high voltage level to the `A14` (`MaixCAM2` is `A6`) pin for the LED to turn on:

```python
from maix import gpio, pinmap, time, sys, err

pin_name = "A6" if sys.device_id() == "maixcam2" else "A14"
gpio_name = "GPIOA6" if sys.device_id() == "maixcam2" else "GPIOA14"

err.check_raise(pinmap.set_pin_function(pin_name, gpio_name), "set pin failed")
led = gpio.GPIO(gpio_name, gpio.Mode.OUT)
led.value(0)

while 1:
    led.toggle()
    time.sleep_ms(500)
```

  * First, get the pin and function name based on the board model.
  * Use `pinmap` to set the pin's function to `GPIO`.
  * `err.check_raise` is used to check the return value of `set_pin_function`. If there's an error, it raises an exception to prevent mistakes.
  * Initialize the `GPIO` object and set it to output mode.
  * The output value is toggled every `0.5s`, causing the LED to blink.

For more API information, please see the [GPIO API documentation](https://wiki.sipeed.com/maixpy/api/maix/peripheral/gpio.html).

## GPIO Input Mode

```python
from maix import gpio, pinmap, time, err

err.check_raise(pinmap.set_pin_function("A19", "GPIOA19"), "set pin failed")
led = gpio.GPIO("GPIOA19", gpio.Mode.IN)

while 1:
    print(led.value())
    time.sleep_ms(1) # sleep to make cpu free
```

## Using the Illumination LED on MaixCAM-Pro

Both `MaixCAM / MaixCAM-Pro` and `MaixCAM2` have a small LED connected to pins `A14` and `IOA6`.
Additionally, the `MaixCAM-Pro` and `MaixCAM2` also have an onboard **illumination LED** connected to pins `B3` and `IOA25`, respectively, which turns on with a high voltage and off with a low voltage:

```python
from maix import gpio, pinmap, time, sys, err

pin_name = "B25" if sys.device_id() == "maixcam2" else "B3"
gpio_name = "B25" if sys.device_id() == "maixcam2" else "GPIOB3"

err.check_raise(pinmap.set_pin_function(pin_name, gpio_name), "set pin failed")
led = gpio.GPIO(gpio_name, gpio.Mode.OUT)
led.value(0)

while 1:
    led.toggle()
    time.sleep_ms(500)

```

## More Examples

See [MaixPy examples](https://github.com/sipeed/MaixPy/tree/main/examples/peripheral/gpio).

## API Documentation

For more API information, see the [GPIO API documentation](https://wiki.sipeed.com/maixpy/api/maix/peripheral/gpio.html).

