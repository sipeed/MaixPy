---
title: LVGL 图形界面
update:
  - date: 2026-11-09
    author: Tao
    version: 1.0.0
    content: 初版文档
---

## 简介

MaixPy 通过 `maix_lvgl` 模块提供 [LVGL](https://lvgl.io/) 9.1.0 的 Python 绑定，写法与 MicroPython 的 `lvgl` 基本一致：

```python
import maix_lvgl as lv
```

`maix_lvgl` 由 MaixCDK 的 LVGL 组件构建，并已随 MaixPy 的 wheel 一起安装，**无需单独安装**。

API 文档：

- [lvgl 模块](/api/maix_lvgl/lvgl.html)
- [lvgl 函数](/api/maix_lvgl/lvgl_functions.html)
- [lvgl 类](/api/maix_lvgl/lvgl_classes.html)
- [maix_lvgl 后端](/api/maix_lvgl/maix_lvgl.html)

## 快速开始

```python
import time
from maix import app, display, touchscreen
import maix_lvgl as lv

disp = display.Display()
ts = touchscreen.TouchScreen()

try:
    lv.init(disp, ts)                 # 传入 MaixPy 的屏幕和触摸屏

    scr = lv.screen_active()
    btn = lv.button(scr)
    btn.set_size(240, 120)
    btn.center()

    label = lv.label(btn)
    label.set_text("Hello MaixCAM2")

    def on_click(event):
        label.set_text("Clicked!")

    btn.add_event_cb(on_click, lv.EVENT.CLICKED, None)

    while not app.need_exit():
        lv.timer_handler()            # 自动推进 LVGL tick
        time.sleep(0.005)
finally:
    lv.deinit()
    ts.close()
    disp.close()
```

运行后屏幕中央会显示一个按钮，点击后文字变为 `Clicked!`。

## 初始化与主循环

`lv.init(display, touchscreen)` 接受 MaixPy 的 `maix.display.Display` 和 `maix.touchscreen.TouchScreen` 对象：

- 不传参数时自动打开屏幕和触摸屏：`lv.init()`
- 只需要屏幕、不需要触摸：`lv.init(disp, False)`

主循环中调用 `lv.timer_handler()`。该函数由 `maix_lvgl` 提供，会先按单调时间推进 `lv_tick_inc()`，再执行 LVGL 的 timer handler。**不要直接使用原生 `lvgl.timer_handler()`**，否则 tick 不会前进，点击和动画都会失效。

退出时调用 `lv.deinit()`；如果 `display`/`touchscreen` 是你自己创建的，还需要分别调用它们的 `close()`。

## 常用控件

```python
scr = lv.screen_active()

# 标签
label = lv.label(scr)
label.set_text("Hello")
label.center()

# 按钮 + 按钮上的标签
btn = lv.button(scr)
btn.set_size(240, 120)
btn.center()
btn_label = lv.label(btn)
btn_label.set_text("Click me")
btn_label.center()

# 滑块
slider = lv.slider(scr)
slider.set_size(200, 20)
slider.center()

# 开关
sw = lv.switch(scr)
sw.center()
```

事件回调和 LVGL 原生写法一致：

```python
def on_click(event):
    print("clicked")

btn.add_event_cb(on_click, lv.EVENT.CLICKED, None)
```

## 屏幕与触摸

- 显示驱动会把 LVGL 渲染到 BGRA8888 缓冲区，再通过 `display.show()` 显示。
- 触摸坐标由 MaixPy 的触摸驱动处理，已经是 640×480 的屏幕坐标。
- 同一时间只能有一个 `maix.display.Display` 使用者。运行前请停止 launcher 或其他占用屏幕的应用。
- 点击目标要足够大，过小的按钮容易点偏。

## 注意事项

- **JPEG 图片**：当前绑定未编入 jpegio（其依赖 LVGL 9.5 的内部接口，与 9.1.0 不兼容），`lv.image` 的 JPEG 解码不可用。
- **中文显示**：默认只启用了 Montserrat 英文字体（与 MaixCDK 的 LVGL 配置一致）。显示中文需要 CJK 点阵字体或 FreeType。
- **版本**：LVGL 9.1.0，绑定生成器参考 [omnipython-lvgl](https://github.com/PyDevices/omnipython-lvgl)。
- 如果自行构建 MaixPy，`setup.py` 会自动构建 `maix_lvgl` 并打包进 MaixPy wheel。
