---
title: MaixCAM MaixPy Quick Start
---

<style>
    #head_links table {
        width: 100%;
        display: table;
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

| Resource Summary           | Link                                                                                      |
| :-------------------------:| :-------------------------------------------------------------------------------------:|
|  Tutorial Documentation 📖 | [wiki.sipeed.com/maixpy/en/](https://wiki.sipeed.com/maixpy/en/)                                   |
| Examples and Source Code <img src="/static/image/github-fill.svg" style="height: 1.5em;vertical-align: middle;"> | [github.com/sipeed/MaixPy](https://github.com/sipeed/MaixPy)                               |
|  MaixCAM Hardware 📷 | [wiki.sipeed.com/maixcam](https://wiki.sipeed.com/maixcam) </br> [wiki.sipeed.com/maixcam-pro](https://wiki.sipeed.com/maixcam-pro)  </br>  [wiki.sipeed.com/maixcam2](https://wiki.sipeed.com/maixcam2)|
|  API Documentation 📚 | [wiki.sipeed.com/maixpy/api/](https://wiki.sipeed.com/maixpy/api/index.html)               |
| MaixHub App Store 📦      | [maixhub.com/app](https://maixhub.com/app)                                                 |
| MaixHub Sharing Square 🎲 | [maixhub.com/share](https://maixhub.com/share)                                             |
| Open Source Projects 📡             | GitHub Search：[MaixCAM](https://github.com/search?q=maixcam&type=repositoriese) / [MaixCAM2](https://github.com/search?q=maixcam2&type=repositoriese) / [MaixPy](https://github.com/search?q=maixpy&type=repositoriese)  |

</div>
<div style="font-size: 1.2em;padding:1em; text-align:center; color: white">
  <div style="padding: 1em 0 0 0">
    <a target="_blank" style="color: white; font-size: 0.9em; border-radius: 0.3em; padding: 0.5em; background-color: #c33d45" href="https://item.taobao.com/item.htm?id=784724795837">Taobao(MaixCAM)</a>
    <a target="_blank" style="color: white; font-size: 0.9em; border-radius: 0.3em; padding: 0.5em; background-color: #c33d45" href="https://item.taobao.com/item.htm?id=846226367137">Taobao(MaixCAM-Pro)</a>
    <a target="_blank" style="color: white; font-size: 0.9em; border-radius: 0.3em; padding: 0.5em; background-color: #c33d45" href="https://www.aliexpress.com/store/911876460">AliExpress</a>
  </div>
</div>
<br>

> For an introduction to MaixPy, please see the [MaixPy official website homepage](../../README.md)
> Please give the [MaixPy project](https://github.com/sipeed/MaixPy) a Star ⭐️ to encourage us to develop more features if you like MaixPy.

<iframe style="width:100%;min-height:30em" src="https://www.youtube.com/embed/qV1lw0UVUYI?si=g3xUX5v3iT9r7RxJ" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

## Quick Preview

<div align="center"><span style="color: #c33d45; font-weight: bold;">MaixCAM2(The Upgraded Version of MaixCAM~)</span></div>
<iframe src="//player.bilibili.com/player.html?isOutside=true&aid=115547387727388&bvid=BV1veCTBsEZa&cid=33995951833&p=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"></iframe>

<div align="center"><span style="color: #c33d45; font-weight: bold;">MaixCAM</span></div>
<iframe src="//player.bilibili.com/player.html?isOutside=true&aid=113485669204279&bvid=BV1ncmRYmEDv&cid=26768769718&p=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true" class="biliiframe"></iframe>

## Before Start

* Please **carefully** follow the steps outlined in this document. Do not skip any sections, and compare your actions accordingly.
* **Pay close attention** to the table of contents on the left. Be sure to read through the basic sections thoroughly and patiently.
* **Before asking questions**, first search the documentation in the left-hand table of contents and review the [FAQ](./faq.md).
* This document is the `MaixPy v4 Tutorial`. Be mindful not to confuse it with the [MaixPy-v1](https://wiki.sipeed.com/soft/maixpy/zh/index.html) (K210 series), and ensure you are referring to the correct documentation.

## Get a MaixCAM/MaixCAM2 Device

![maixcam2](https://wiki.sipeed.com/static/image/maixcam2_front_back.png)


Basic Information:[MaixCAM2 Introduction & Resources](https://wiki.sipeed.com/hardware/en/maixcam/maixcam2.html)
Purchase Links:[Sipeed Taobao](https://item.taobao.com/item.htm?id=846226367137) or [Sipeed AliExpress](https://www.aliexpress.com/store/911876460)
<br>

![maixcam_pro](../../static/image/maixcam_pro.png)

**MaixCAM** currently has several versions. Choose according to your needs:

| | |
|---|---|
|**MaixCAM-Pro**(Recommended)|Baisc Infomation:[MaixCAM-Pro Introduction & Resources](https://wiki.sipeed.com/maixcam-pro)<br>Purchase Links:[Sipeed Taobao](https://item.taobao.com/item.htm?id=846226367137) or [Sipeed AliExpress](https://www.aliexpress.com/store/911876460)|
|**MaixCAM**|Baisc Infomation:[MaixCAM Introduction & Resources](https://wiki.sipeed.com/maixcam)<br>Purchase Links:[Sipeed Taobao](https://item.taobao.com/item.htm?id=784724795837) or [Sipeed AliExpress](https://www.aliexpress.com/store/911876460)|
|**MaixCAM-Lite**(Not Recommended)|Screenless and caseless version, more affordable. Not recommended for learning/development, but may be considered for mass production.|

<br>

>! Note that currently only the MaixCAM development board is supported. Other development boards with the same chip are not supported, including Sipeed's development boards with the same chip. Please be careful not to purchase the wrong board, which could result in unnecessary waste of time and money.


## Getting Started

Please select the documentation corresponding to your hardware platform to proceed:

|硬件平台|上手文档|
|-|-|
|MaixCAM Lite|[Quick Start MaixCAM(Screenless Version)](./README_no_screen.md)|
|MaixCAM/MaixCAM Pro|[Quick Start MaixCAM](./README_MaixCAM.md)|
|MaixCAM2|[Quick Start MaixCAM2](./README_MaixCAM2.md)|

 ## Next Steps

 If you like what you've seen so far, **please be sure to give the MaixPy open-source project a star on [GitHub](https://github.com/sipeed/MaixPy) (you need to log in to GitHub first). Your star and recognition is the motivation for us to continue maintaining and adding new features!**

 Up to this point, you've experienced the usage and development workflow. Next, you can learn about `MaixPy` syntax and related features. Please follow the left sidebar to learn. If you have any questions about using the API, you can look it up in the [API documentation](/api/).

 It's best to learn with a specific purpose in mind, such as working on an interesting small project. This way, the learning effect will be better. You can share your projects and experiences on the [MaixHub Share Plaza](https://maixhub.com/share) and receive cash rewards!


## Frequently Asked Questions (FAQ)

If you encounter any problems, please check the [FAQ](./faq.md) first. If you cannot find a solution there, you can ask in the forums or groups below, or submit a source code issue on [MaixPy issue](https://github.com/sipeed/MaixPy/issues).

 ## Share and Discuss

 * **[MaixHub Project and Experience Sharing](https://maixhub.com/share)**: Share your projects and experiences, and receive cash rewards. The basic requirements for receiving official rewards are:
   * **Reproducible**: A relatively complete process for reproducing the project.
   * **Showcase**: No detailed project reproduction process, but an attractive project demonstration.
   * **Bug-solving experience**: Sharing the process and specific solution for resolving a particular issue.
 * [MaixPy Official Forum](https://maixhub.com/discussion/maixpy) (for asking questions and discussion)
 * Telegram: [MaixPy](https://t.me/maixpy)
 * MaixPy Source Code Issues: [MaixPy issue](https://github.com/sipeed/MaixPy/issues)
 * For business cooperation or bulk purchases, please contact support@sipeed.com.
