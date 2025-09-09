---
title: MaixCAM MaixPy 播放音频
update:
  - date: 2024-05-20
    author: lxowalle
    version: 1.0.0
    content: 初版文档
---

## 简介

本文档提供播放音频的使用方法


## 使用方法

### 硬件支持情况

| 设备        | 麦克风 | 喇叭 |
| ----------- | ------ | ---- |
| MaixCAM     | ✅      | ❌    |
| MaixCAM2    | ✅      | ✅    |
| MaixCAM Pro | ✅      | ✅    |

### 硬件操作

![image-20240520134637905](../../../static/image/maixcam_hardware_back.png)

`MaixCAM`没有内置喇叭，因此需要自行焊接一个功率在`1W`内的喇叭。喇叭焊接的引脚见上图的Speaker对应的`VOP`和`VON`脚。

注：如果`MaixCAM`在这两个脚上连接了铜柱，则可以直接焊接在铜柱上，为了美观也可以焊接在板子的另一面。

### 编写代码

#### 播放一个`WAV`文件

```python
from maix import audio, time, app

p = audio.Player("/root/output.wav")

p.play()
p.volume(80)
while not app.need_exit():
    time.sleep_ms(10)
print("play finish!")
```

步骤：


1. 导入audio、time和app模块

   ```python
   from maix import audio, time, app
   ```

2. 初始化播放器

   ```python
   p = audio.Player("/root/output.wav")
   p.volume(80)
   ```

  - 默认的采样率是48k，采样格式为小端格式-有符号16位，采样通道为1。你也可以像这样自定义参数`p = audio.Player(sample_rate=48000, format=audio.Format.FMT_S16_LE, channel = 1)`。目前只测试过采样率48000，`FMT_S16_LE`格式，和采样通道数为1。
  - 如果是`.wav`文件，则会自动获取采样率、采样格式和采样通道。
  - `p.volume(80)`设置音量为80，范围为[0~100]。

3. 播放音频

   ```python
   p.play()
   ```

  - 该操作将会阻塞直到写入所有音频数据，但不会阻塞到实际播放完所有音频数据。如果调用`play()`后退出了程序，则部分待播放的音频数据可能会丢失。

4. 完成



#### 用`PCM`数据播放

```python
from maix import audio, time, app

p = audio.Player()

with open('/root/output.pcm', 'rb') as f:
    ctx = f.read()

p.play(bytes(ctx))

while not app.need_exit():
    time.sleep_ms(10)

print("play finish!")
```

步骤：


1. 导入audio、time和app模块

   ```python
   from maix import audio, time, app
   ```

2. 初始化播放器

   ```python
   p = audio.Player()
   ```
  - 注意默认的采样率是48k，采样格式为小端格式-有符号16位，采样通道为1。你也可以像这样自定义参数`p = audio.Player(sample_rate=48000, format=audio.Format.FMT_S16_LE, channel = 1)`。目前只测试过采样率48000，`FMT_S16_LE`格式，和采样通道数为1

3. 打开并播放一个PCM文件

   ```python
     with open('/root/output.pcm', 'rb') as f:
         ctx = f.read()
   
     p.play(bytes(ctx))
   
     while not app.need_exit():
       time.sleep_ms(10)
   ```

  - `with open('xxx','rb') as f:`打开文件`xxx`， 并获取文件对象`f`
  - `ctx = f.read()`将读取文件的内容到`ctx`中
  - `p.play(bytes(ctx))`播放音频，`p`是已打开的播放器对象， `ctx`是转换为bytes类型的`PCM`数据
  - `time.sleep_ms(10)`这里有一个循环来等待播放完成，因为播放操作是异步执行的，如果提前退出了程序，那么可能导致音频不会完全播放。

4. 完成

#### 非阻塞播放

当做语音助手, 实时通信等场景时通常需要播放音频的过程不能阻塞主线程, 因此可以将`Player`设置为非阻塞模式,并添加一些应用层代码来支持播放时不阻塞主线程的方法. 参考示例如下:

```python
from maix import audio, app, time
import threading
from queue import Queue, Empty

class StreamPlayer:
    def __init__(self, sample_rate=16000, channel=1, block:bool=False):
        self.p = audio.Player(sample_rate=sample_rate, channel=channel, block=block)
        self.p.volume(50)
        zero_data = bytes([0] * 4096)
        self.p.play(zero_data)
        self.queue = Queue(maxsize=250)
        self.t = threading.Thread(target=self.__thread, daemon=True)
        self.t.start()

    def wait_idle_size(self, size:int):
        while not app.need_exit():
            idle_frames = self.p.get_remaining_frames()
            write_frames = size / self.p.frame_size()
            if idle_frames >= write_frames:
                break
            time.sleep_ms(10)

    def __thread(self):
        while not app.need_exit():
            try:
                pcm = self.queue.get(timeout=500)
                # wait player is idle
                self.wait_idle_size(len(pcm))
                self.p.play(pcm)
            except Empty:
                continue

    def write(self, pcm:bytes):
        remain_len = len(pcm)
        period_bytes = self.p.frame_size() * self.p.period_size()
        offset = 0
        while remain_len > 0:
            write_bytes = period_bytes if period_bytes <= remain_len else period_bytes - remain_len
            new_pcm = pcm[offset:offset+write_bytes]
            self.queue.put(new_pcm)
            remain_len -= write_bytes
            offset += write_bytes

    def wait_finish(self):
        total_frames = self.p.period_count() * self.p.period_size()
        while not app.need_exit():
            idle_frames = self.p.get_remaining_frames()
            if idle_frames == total_frames:
                break
            time.sleep_ms(10)

if __name__ == '__main__':
    stream_player = StreamPlayer()
    with open('/maixapp/share/audio/demo.wav', 'rb') as f:
        pcm = f.read()
        t = time.ticks_ms()
        stream_player.write(pcm)
        print(f'write pcm data cost {time.ticks_ms() - t} ms')

        t = time.ticks_ms()
        stream_player.wait_finish()
        print(f'write play finish cost {time.ticks_ms() - t} ms')
```

这个示例里通过`block`参数将`Player`对象设置为了非阻塞模式, 因此调用`play()`方法时不会阻塞主线程

由于内部的缓存大小的限制, 如果一定时间内播放的数据量大于缓冲量时, 还是会阻塞在`play`方法中, 因此可以通过`get_remaining_frames()`方法来获取buffer剩余空间的大小, 需要注意该方法返回的单位为`帧`, 通过`frame_size()`方法可以将要`帧`转换为`字节`

```python
remaining_frames = p.get_remaining_frames()		# unit:frame
remaining_bytes = p.frame_size(remaining_frames) # unit: bytes
```

可以将播放操作放在另一个线程中, 并且可以播放前检查如果剩余空间足够时, 再调用`play()`来播放, 这样就能保证一定不会阻塞主线程.
