<div align="center">

# _AstrBot Admin Tools Plugin_

![views](https://count.getloli.com/get/@astrbotneteasemusic?theme=booru-jaypee)<br>

_✨ 作者：[SatenShiroya](https://github.com/SatenShiroya)✨_

[![Plugin Version](https://img.shields.io/badge/Version-V2.1.0-blue.svg)](https://github.com/SatenShiroya/astrbot_plugin_neteasecloud_music)
[![AstrBot](https://img.shields.io/badge/AstrBot-Plugin-ff69b4)](https://github.com/AstrBotDevs/AstrBot)
[![License](https://img.shields.io/badge/License-AGPL%203.0-green.svg)](LICENSE)

</div>

## ✨ _介绍_

- 一个轻量级 AstrBot 插件，支持通过自然语言让 AI 自动为你在 **QQ 中点播网易云音乐**。
- 利用 LLM 工具调用能力，智能识别歌名与歌手，自动搜索并发送官方音乐卡片。
- **特别优化海外用户支持**：可配置 HTTP/SOCKS 代理绕过地域限制。

> ⚠️ 注意：本插件**仅在 QQ 平台生效**（需配合 NapCat/QQNT 协议端），其他平台将返回友好提示。

## ⌨️ _使用说明_

- 直接使用自然语言点歌，例如：
  - “我想听孙燕姿的绿光”
  - “我想听稻香”
- AI 会自动调用工具，搜索网易云音乐，并在 QQ 聊天中发送**官方音乐卡片**（带封面、播放按钮）。

## 🌍 _海外用户必看_

- 如果你部署在海外服务器，可能会遇到“找不到歌曲”或返回加密数据的问题。  
- **解决方案**：在插件配置中填写中国大陆的代理地址（HTTP 或 SOCKS）。

- 支持格式示例：
  - `http://1.2.3.4:8080`
  - `http://user:pass@1.2.3.4:8080`
  - `socks5://1.2.3.4:1080`
- 使用 SOCKS 代理需额外安装依赖： 
   
> ```bash
> pip install aiohttp-socks
> ```

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

- ### _V 2.1.0_（当前版本）
  - 点歌超时后行为修改为自动发送第一首

- ### _V 2.0.0_
  - 新增`music_select`配置项，开启后可以让bot优先回复播放列表，再回复序号选择准确歌曲
  - 新增`select_wait_time``search_limit`配置项，用户可以自行选择搜索歌曲返回数量和回复结果等待时间
  - 使用嵌套配置项以优化配置页面显示效果
  - 优化了搜索结果对LLM的返回，解决之前插件调用后日志显示警告`工具没有返回结果或直接将结果发送给用户`的问题

- ### _V 1.4.0_
  - 新增 `qq_platform` 配置项，可强制让bot在任何平台发送音乐卡片，不支持平台可能失败

- ### _V 1.3.0_
  - 新增 `proxy_url` 配置项，支持 HTTP/HTTPS/SOCKS 代理，提升海外用户可用性

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