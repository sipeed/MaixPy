---
title: Using Key Events in MaixCAM MaixPy
update:
  - date: 2025-01-08
    version: v1.0
    author: neucrack
    content: Added documentation
---

## Introduction

MaixCAM is equipped with built-in buttons, including the user/ok button and the power button.  
By default, the user/ok button acts as an exit button in MaixPy. Pressing it automatically calls `maix.app.set_exit_flag(True)`.  
If your program relies on `maix.app.need_exit()` to determine when to exit, pressing the button will cause the program to terminate.

Additionally, you can customize the button's behavior. Once customized, the default behavior of setting the exit flag will be disabled.

## Reading Key Events in MaixCAM MaixPy

### Default Behavior: Exit Flag Set When Button is Pressed

The default behavior works without explicit function calls:
```python
from maix import app, time

cout = 0
while not app.need_exit():
    time.sleep(1)
    print(cout)
    cout += 1
```
Pressing the button will exit the loop.

### Reading Key Events and Customizing Callback Functions

You can use the `key.Key` class to handle key events. The callback function takes two parameters:
- `key_id`: The key's ID. Refer to [maix.key.Keys API Documentation](/api/maix/peripheral/key.html#Keys). For custom drivers, the ID depends on the driver.
- `state`: The key's state. Refer to [maix.key.State API Documentation](/api/maix/peripheral/key.html#State).

Example:
```python
from maix import key, app, time

def on_key(key_id, state):
    '''
        this func is called in a single thread
    '''
    print(f"key: {key_id}, state: {state}") # key.c or key.State.KEY_RELEASED

key_obj = key.Key(on_key)

while not app.need_exit():
    time.sleep(1)
```

A more complete example:
```python
from maix import image, key, app, display

class App:
    def __init__(self):
        self.key_obj = key.Key(self.on_key)
        self.disp = display.Display()
        self.key_id = 0
        self.state = 0

    def on_key(self, key_id, state):
        '''
            This function is called in a single thread
        '''
        print(f"key: {key_id}, state: {state}") # e.g., key.c or key.State.KEY_RELEASED
        self.key_id = key_id
        self.state = state

    def run(self):
        while not app.need_exit():
            img = image.Image(self.disp.width(), self.disp.height(), image.Format.FMT_RGB888)
            msg = f"key: {self.key_id}, state: {self.state}"
            img.draw_string(0, 10, msg, image.Color.from_rgb(255, 255, 255), 1.5)
            self.disp.show(img)

App().run()
```

## Customizing Key Drivers

MaixPy is based on a Linux system, allowing you to write custom key drivers. You can add your custom key devices to the `key_devices` field in `/boot/board`. Multiple devices are supported and can be separated by commas, e.g.:  
`key_devices:/dev/my_keys1,/dev/my_keys2`.

### Driver Development Methods

1. **Kernel Driver**  
   Follow the standard Linux driver development process, using a cross-compilation toolchain to compile a `.ko` driver file. Load the driver automatically at boot via `/etc/init.d`.

2. **User-Space Driver**  
   For buttons connected to GPIO pins, you can write a user-space driver using the GPIO API. Use `/dev/uinput` to export a device file.  
   - This approach requires a program to continuously read GPIO inputs.  
   - The program can be integrated into your main application or run as a standalone background process, offering flexibility.
