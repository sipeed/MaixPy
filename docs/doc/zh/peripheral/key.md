---
title: MaixCAM MaixPy 按键事件使用
update:
  - date: 2025-01-08
    version: v1.0
    author: neucrack
    content: 添加文档
---

## 简介

MaixCAM 机身自带了按键，包括 user/ok 按键，电源按键等。
默认 user/ok 按键在 MaixPy 中是退出按钮，按下会自动调用`maix.app.set_exit_flag(True)`，如果你的程序调用了`maix.app.need_exit()`作为退出依据，则按下按键就会退出程序。

另外，你也可以自定义按键的作用，自定义后上面说的默认的设置退出标志行为就会取消。


## MaixCAM MaixPy 中读取按键

### 默认行为，即按下会设置程序退出标志

无需显示调用，默认就有：
```python
from maix import app, time

cout = 0
while not app.need_exit():
    time.sleep(1)
    print(cout)
    cout +=1
```
按下按键就会退出循环了。

### 读取按键事件和自定义回调函数

使用`key.Key`类即可，回调函数有两个参数：
* `key_id`: 按键 ID，取值看[maix.key.Keys API 文档](/api/maix/peripheral/key.html#Keys)，自定义的驱动由驱动决定。
* `state`: 按键状态，取值看[maix.key.State API 文档](/api/maix/peripheral/key.html#State)。


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

完善一些的例程：

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
            this func called in a single thread
        '''
        print(f"key: {key_id}, state: {state}") # key.c or key.State.KEY_RELEASED
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

## 自定义按键驱动

MaixPy 基于 Linux 系统，你可以给系统编写按键驱动，然后在`/boot/board` 里面将自己的按键设备添加到`key_devices`键值中，支持多个设备，多个设备用逗号隔开，比如：
`key_devices:/dev/my_keys1,/dev/my_keys2`。

驱动编写方法：
* 方法一：内核驱动，按照通用的 Linux 驱动开发方法，使用交叉编译工具链编译出 `ko`驱动文件，开机在`/etc/init.d` 中自动加载。
* 方法二：用户层驱动，比如你的按键接到了 GPIO 上，可以直接基于 GPIO API 编写，使用`/dev/uinput`导出一个设备文件即可，具体方法可以自行搜索，这种方法需要有读取 GPIO 代码一直在运行，可以和你的程序写到一起，也可以单独写一个程序运行在后台，比较灵活。


