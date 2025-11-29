<div align="center">

# _AstrBot Admin Tools Plugin_

![views](https://count.getloli.com/get/@astrbotneteasemusic?theme=booru-jaypee)<br>

_✨ 作者：[SatenShiroya](https://github.com/SatenShiroya)✨_

[![Plugin Version](https://img.shields.io/badge/Version-V1.2.0-blue.svg)](https://github.com/SatenShiroya/astrbot_plugin_neteasecloud_music)
[![AstrBot](https://img.shields.io/badge/AstrBot-Plugin-ff69b4)](https://github.com/AstrBotDevs/AstrBot)
[![License](https://img.shields.io/badge/License-AGPL%203.0-green.svg)](LICENSE)

</div>

## ✨ _介绍_

- 一个简单的Astrbot插件，实现通过自然语言调用AI进行网易云点歌
- 仅适用于QQ平台

## ⌨️ _使用说明_

- 直接使用自然语言点歌，例如：
  - “我想听孙燕姿的绿光”
  - “我想听稻香”
- AI 会自动搜索网易云音乐列表中的第一首结果并返回播放卡片。

## 📌 _效果_

<div align="center">
  <img src="effect.jpg" alt="效果图，图裂了就来仓库看">
</div>

## 📦 _安装_

 - **推荐方式**：在 AstrBot 的插件市场中搜索 `astrbot_plugin_NetEaseCloud_Music`，点击安装并等待完成。
 - **手动安装**：下载 ZIP 文件，在 AstrBot 管理界面中通过“本地压缩包”方式上传安装。

## 📝 _版本变更履历_ 

<details>
<summary style="padding-left: 1.6em;"><em>点此展开显示</em></summary>

- ### _V 1.2.0_
  - 为网易云搜索增加自动重试机制，提升稳定性。
  - 移除已失效的非 QQ 平台的音频链接兜底措施，仅保留 QQ 音乐卡片支持。
  - 非 QQ 平台现返回友好提示，引导用户在 QQ 中使用点歌功能。
  - 增强搜索结果解析的健壮性，防止因数据异常导致崩溃。


- ### _V 1.1.0_
  - 新增自定义点歌成功回复配置项


- ### _V 1.0.0_
  - 首次发布

</details>

## 🔗 _相关链接_

- 机器人框架：[AstrBot 官方文档](https://astrbot.app)
- 客户端使用：[Napcat 官方文档](https://napcat.napneko.icu/)

## 👥 _贡献指南_

- ⭐️&nbsp; Star 这个项目！（点右上角的星星，感谢支持！）
- 🐞&nbsp; 提交 Issue 报告问题
- 🔧&nbsp; 提交 Pull Request 改进代码
- 🧠&nbsp; 提出新功能建议