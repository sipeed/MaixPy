---
title: 参与 MaixCAM MaixPy 文档修改和贡献代码
---

## 参与 MaixPy 文档修改

* 点击要修改的文档右上角的`编辑本页`按钮，进入 github 源文档页面。
* 保证已经登录了 GitHub 账号。
* 在 github 预案文档页面点击右上角铅笔按钮修改文档内容。
* github 会提示需要 fork 一份到自己的仓库，点击 fork 按钮。
> 这一步就是将 MaixPy 源码仓库复刻一份到你自己的账号下，这样你就可以自由修改了。
* 修改文档内容，然后在页面底部填写修改说明，点击提交修改。
* 然后在你的仓库中找到 Pull requests 按钮，点击创建一个 Pull requests。
* 然后在弹出的页面中填写修改说明，点击提交 Pull requests，其它人和管理员就可以在[Pull requests 页面](https://github.com/sipeed/MaixPy/pulls)看到你的修改了。
* 等待管理员审核通过后，你的修改就会合并到 MaixPy 源码仓库中了。
* 合并成功后，文档会自动更新到 [MaixPy 官方文档](https://wiki.sipeed.com/maixpy)。
> 文档经过 CDN 缓存了的，可能需要等待一段时间才能看到更新，紧急更新可以联系管理员手动刷新。
> 也可以访问 [en.wiki.sipeed.com/maixpy](https://en.wiki.sipeed.com/maixpy) 查看 github pages 服务版本，这个是没有缓存实时更新的。


## 参与 MaixPy 代码贡献

* 访问 MaixPy 代码仓库地址：[github.com/sipeed/MaixPy](https://github.com/sipeed/MaixPy)
* 在修改代码前最好先创建一个 [issue](https://github.com/sipeed/MaixPy/issues) ，描述你要修改的内容让大家知道你的想法和计划，这样大家可以参与修改讨论，以免重复劳动。
* 点击右上角的 fork 按钮，将 MaixPy 代码仓库复刻一份到你自己的账号下。
* 然后在你的账号下 clone 一份代码到本地。
* 修改代码后提交到你的仓库中。
* 然后在你的仓库中找到 Pull requests 按钮，点击创建一个 Pull requests。
* 然后在弹出的页面中填写修改说明，点击提交 Pull requests，其它人和管理员就可以在[Pull requests 页面](https://github.com/sipeed/MaixPy/pulls)看到你的修改了。
* 等待管理员审核通过后，你的修改就会合并到 MaixPy 源码仓库中了。

> 需要注意的是 MaixPy 的代码大多数是从 [MaixCDK](https://github.com/sipeed/MaixCDK) 自动生成的，所以如果你修改 C/C++ 源码，很有可能你需要先修改这个仓库。


