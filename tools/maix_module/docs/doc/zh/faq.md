---
title: MaixPy FAQ(常见问题)
---

此页面列出了 MaixPy 相关的常见问题和解决方案，如果你遇到了问题，请先在这里找寻答案。
如果这个页面找不到答案，可以到 [MaixHub 讨论版块](https://maixhub.com/discussion) 将问题的详细步骤发贴提问。

MaixPy 相关问题参考 [MaixPy FAQ](https://wiki.sipeed.com/maixpy/doc/zh/faq.html)
如果你使用的是 MaixCAM, 也可以参考 [MaixCAM FAQ](https://wiki.sipeed.com/hardware/zh/maixcam/faq.html)

## 如何安装

* 下载编译好的 `xxx.whl` 文件。
* 上传文件到设备，比如上传到`/root`目录下。
* 执行 Python 代码。
```python
import os

os.system("pip install /root/xxx.whl")
```

