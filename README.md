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

- ### [v2.1.0] - fix: 修改点歌超时处理逻辑
  - 🛠️ 列表点歌超时逻辑由退出点歌修改为发送列表第一首

- ### [v2.0.0] - feat: 新增交互式选歌模式与多项配置优化
  - ✨ 新增 `music_select` 配置项，开启后 Bot 将优先回复播放列表，用户可通过序号精准选择歌曲。
  - ✨ 新增 `select_wait_time` 与 `search_limit` 配置项，支持用户自定义搜索结果数量及响应等待时间。
  - 🛠️ 重构为嵌套式配置结构，显著提升配置页面的可读性与操作体验。
  - 🛠️ 优化搜索结果对 LLM 的返回格式，彻底解决插件调用时日志报错 `工具没有返回结果或直接将结果发送给用户` 的问题。

- ### [v1.4.0] - feat: 新增跨平台音乐卡片强制发送支持
  - ✨ 新增 `qq_platform` 配置项，支持强制在所有平台尝试发送音乐卡片（注：部分不支持的平台可能会发送失败）。

- ### [v1.3.0] - feat: 支持多协议代理配置
  - ✨ 新增 `proxy_url` 配置项，全面支持 HTTP/HTTPS/SOCKS 代理协议，显著改善海外用户的使用体验。

- ### [v1.2.0] - fix: 增强搜索稳定性与平台兼容性处理
  - 🛠️ 为网易云音乐搜索引入自动重试机制，有效应对网络波动。
  - 🛠️ 移除已失效的非 QQ 平台音频链接兜底策略，聚焦于 QQ 音乐卡片的核心支持。
  - ✨ 针对非 QQ 平台用户返回友好的引导提示，建议其在 QQ 环境中使用点歌功能。
  - 🛠️ 强化搜索结果解析逻辑，防止因数据异常导致插件崩溃。

- ### [v1.1.0] - feat: 支持自定义点歌成功回复
  - ✨ 新增自定义点歌成功后的回复内容配置项，满足多样化需求。

- ### [v1.0.0] - feat: 项目首次发布
  - ✨ 正式发布点歌插件基础功能。

</details>

## 🔗 _相关链接_

- 机器人框架：[AstrBot 官方文档](https://astrbot.app)
- 客户端使用：[Napcat 官方文档](https://napcat.napneko.icu/)

## 👥 _贡献指南_

- ⭐️&nbsp; Star 这个项目！（点右上角的星星，感谢支持！）
- 🐞&nbsp; 提交 Issue 报告问题
- 🔧&nbsp; 提交 Pull Request 改进代码
- 🧠&nbsp; 提出新功能建议