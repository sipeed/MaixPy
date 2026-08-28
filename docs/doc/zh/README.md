---
title: 快速开始
---

<style>
    #head_links table {
        width: 100%;
        display: table;
    }
    .biliiframe {
      width: 100%;
      min-height: 30em;
      border-radius: 0.5em;
      border: 1em solid white;
  }
    @media screen and (max-width: 900px){
      #head_links th, #head_links td {
          /* padding: 8px; */
          font-size: 0.9em;
          padding: 0.1em 0.05em;
      }
    }
</style>

<div id="head_links">

| 资源汇总                    | 链接                                                                                      |
| :-------------------------: | :-------------------------------------------------------------------------------------:|
|  MaixPy 教程文档 📖         | [wiki.sipeed.com/maixpy](https://wiki.sipeed.com/maixpy)                                   |
| MaixPy 例程和源码 ![GitHub](/static/image/github-fill.svg)           | [github.com/sipeed/MaixPy](https://github.com/sipeed/MaixPy)                               |
|  MaixCAM 硬件资料 📷        | [wiki.sipeed.com/maixcam](https://wiki.sipeed.com/maixcam) </br> [wiki.sipeed.com/maixcam-pro](https://wiki.sipeed.com/maixcam-pro)  </br>  [wiki.sipeed.com/maixcam2](https://wiki.sipeed.com/maixcam2)                             |
|  MaixPy API 文档 📚        | [wiki.sipeed.com/maixpy/api/](https://wiki.sipeed.com/maixpy/api/index.html)               |
| MaixPy 视频和教程 💿        | [B站搜 MaixCAM 或 MaixPy](https://search.bilibili.com/all?keyword=maixcam&from_source=webtop_search&spm_id_from=333.1007&search_source=5) |
| MaixHub 应用商店 📦     | [maixhub.com/app](https://maixhub.com/app)                                                 |
| MaixHub 分享广场 🎲       | [maixhub.com/share](https://maixhub.com/share)                                             |
| 开源项目 📡             | GitHub 搜：[MaixCAM](https://github.com/search?q=maixcam&type=repositories) / [MaixCAM2](https://github.com/search?q=maixcam2&type=repositories) / [MaixPy](https://github.com/search?q=maixpy&type=repositories)  |

</div>
<div style="font-size: 1.2em;padding:1em; text-align:center; color: white">
  <div style="padding: 1em 0 0 0">
    <a target="_blank" style="color: white; font-size: 0.9em; border-radius: 0.3em; padding: 0.5em; background-color: #c33d45" href="https://item.taobao.com/item.htm?id=784724795837">淘宝(MaixCAM)</a>
    <a target="_blank" style="color: white; font-size: 0.9em; border-radius: 0.3em; padding: 0.5em; background-color: #c33d45" href="https://item.taobao.com/item.htm?id=846226367137">淘宝(MaixCAM-Pro)</a>
    <a target="_blank" style="color: white; font-size: 0.9em; border-radius: 0.3em; padding: 0.5em; background-color: #c33d45" href="https://www.aliexpress.com/store/911876460">速卖通</a>
  </div>
</div>
<br>

> 关于 MaixPy 介绍请看 [MaixPy 官网首页](../../README.md)
> 喜欢 MaixPy 请给 [ MaixPy 项目](https://github.com/sipeed/MaixPy) 点个 Star ⭐️ 以鼓励我们开发更多功能。

## 先选择你的设备

>! **先确认设备型号，再点击下面对应的快速开始。三种设备的启动和连接方法不同，请不要混着看。** 型号可以在包装、订单名称或设备外壳上找到。

| 你的设备 | 产品图 | 现在打开这篇教程 |
| --- | --- | --- |
| **MaixCAM2** | ![MaixCAM2](/static/image/maixcam2_front_back.png) | **[👉 打开 MaixCAM2 快速开始](./README_MaixCAM2.md)** |
| **MaixCAM / MaixCAM-Pro** | ![MaixCAM / MaixCAM-Pro](/static/image/maixcams.png) | **[👉 打开 MaixCAM 快速开始](./README_MaixCAM.md)** |
| **MaixCAM Lite / 其他无屏幕版本** | ![MaixCAM Lite / 无屏幕版本](/static/image/maixcam.png) | **[👉 打开无屏幕版快速开始](./README_no_screen.md)** |

## 开始前了解这些

- 本站是 `MaixPy v4` 文档，适用于 MaixCAM 系列。K210 系列请看 [MaixPy v1 文档](https://wiki.sipeed.com/soft/maixpy/zh/index.html)。
- 即使芯片型号相同，其他开发板也不能直接使用本文档中的系统和程序。
- 视频适合快速了解操作，具体按钮和参数请以最新文档为准。更多视频可以在 [B 站搜索 MaixCAM 或 MaixPy](https://search.bilibili.com/all?keyword=maixcam)。
- 遇到问题时，先查看对应步骤和 [FAQ](./faq.md)。

<iframe src="//player.bilibili.com/player.html?isOutside=true&aid=112865415531014&bvid=BV1vcvweCEEe&cid=500001630687957&p=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true" style="min-height:20em; width: 90%"></iframe>

## 完成快速开始后学什么

按照设备对应的快速开始文档完成开机、联网和运行例程后，可以根据目标继续：

- **第一次写 MaixPy 程序**：先看左侧“基础”栏目中的 [MaixVision 使用](./basic/maixvision.md)和 [Python 基础知识](./basic/python.md)。
- **想使用摄像头、屏幕或常见算法**：从左侧“基础图像和算法”选择需要的功能。
- **想运行或训练 AI 模型**：从左侧“AI 视觉”和“训练、转换和部署”开始。
- **想把程序放到设备菜单中**：查看[应用开发和应用商店](./basic/app.md)。

函数的参数和返回值可以在 [API 文档](/api/)中查询。带着一个具体目标学习会更容易，例如先做一个识别二维码或检测苹果的小项目。

## 常见问题 FAQ

遇到问题可以优先在 [FAQ](./faq.md) 里面找，找不到再在下面的论坛或者群询问，或者在 [MaixPy issue](https://github.com/sipeed/MaixPy/issues) 提交源码问题。

## 分享交流

* **[MaixHub 项目和经验分享](https://maixhub.com/share)**：欢迎分享你的项目和实践经验，还有机会获得官方现金奖励。官方主要鼓励以下三类内容：
  * **完整教程**：提供比较完整的制作步骤，让其他人可以跟着做出来。
  * **作品展示**：不要求提供完整的制作步骤，重点展示项目的创意和实际效果。
  * **问题解决经验**：记录遇到的问题、排查过程和最终解决方法。
* [MaixPy 官方论坛](https://maixhub.com/discussion/maixpy)（提问和交流）
* QQ 群： （建议在 QQ 群提问前先发个帖，方便群友快速了解你需要了什么问题，复现过程是怎样的）
  * MaixPy (v4) AI 视觉交流大群: 862340358
* Telegram: [MaixPy](https://t.me/maixpy)
* MaixPy 源码问题: [MaixPy issue](https://github.com/sipeed/MaixPy/issues)
* 商业合作或批量购买请联系 support@sipeed.com 。
