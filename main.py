import json
import aiohttp
import asyncio
import time
from typing import Dict, Any, List
from astrbot.api.event import filter
from astrbot.core.message.message_event_result import MessageEventResult
from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import AiocqhttpMessageEvent
from astrbot.api.star import Star, register, Context
from astrbot.api import logger, AstrBotConfig
from astrbot.core.message.components import Plain

USER_STATES: Dict[int, Dict[str, Any]] = {}

@register("astrbot_plugin_NetEaseCloud_Music", "SatenShiroya", "网易云音乐点歌插件：支持列表选择", "2.0.0")
class MusicPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.session = None

        templates_config = config.get("message_templates", {})
        self.play_success_message_template = templates_config.get(
            "play_success", "已为您播放《{title}》"
        )
        self.select_success_template = templates_config.get(
            "select_success", "这就为您播放第 {index} 首：《{title}》"
        )
        self.select_error_template = templates_config.get(
            "select_error", "点歌序号只能在 1 到 {max_idx} 之间，请重新输入"
        )
        self.select_cancel_template = templates_config.get(
            "select_cancel", "回复内容非法，已取消点歌操作"
        )

        network_config = config.get("network", {})
        self.proxy_url = network_config.get("proxy_url", "")
        self.is_qq_platform = network_config.get("is_qq_platform", True)

        features_config = config.get("features", {})
        self.music_select = features_config.get("music_select", False)
        self.select_wait_time = features_config.get("select_wait_time", 30)
        
        raw_limit = features_config.get("search_limit", 5)
        if not isinstance(raw_limit, int) or raw_limit < 1:
            self.search_limit = 5
        elif raw_limit > 10:
            self.search_limit = 10
            logger.warning("[NetEaseMusic] 配置的 search_limit 超过最大值 10，已自动修正为 10。")
        else:
            self.search_limit = raw_limit
            
        logger.info(f"[NetEaseMusic] 当前搜索限制设置为：{self.search_limit}")

    async def initialize(self):
        """插件初始化：建立 aiohttp 会话"""
        connector = None

        if self.proxy_url and self.proxy_url.startswith(("socks4://", "socks5://")):
            try:
                from aiohttp_socks import ProxyConnector
                connector = ProxyConnector.from_url(self.proxy_url)
                logger.info("[NetEaseMusic] 已启用 SOCKS 代理连接器")
            except ImportError:
                logger.error(
                    "[NetEaseMusic] 检测到 SOCKS 代理，但未安装依赖 'aiohttp-socks'！\n"
                    "请运行: pip install aiohttp-socks\n"
                    "将回退到无代理模式。"
                )
                self.proxy_url = "" 

        self.session = aiohttp.ClientSession(connector=connector, trust_env=False)
        logger.info("[NetEaseMusic] 插件初始化完成")

    async def terminate(self):
        """
        插件销毁：关闭 aiohttp 会话并清理所有用户状态
        """
        logger.info("[NetEaseMusic] 正在清理资源...")
        
        if self.session:
            await self.session.close()
            logger.info("[NetEaseMusic] aiohttp 会话已关闭")

        for uid in list(USER_STATES.keys()):
            self._cancel_user_state(uid)
            
        logger.info("[NetEaseMusic] 资源清理完毕")

    async def _netease_request(self, url: str, data: dict = None, method: str = "GET"):
        """统一请求方法"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://music.163.com/",
            "Origin": "https://music.163.com",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        cookies = {"appver": "2.9.11", "os": "pc"}

        proxy = (
            self.proxy_url
            if self.proxy_url and self.proxy_url.startswith(("http://", "https://"))
            else None
        )

        timeout = aiohttp.ClientTimeout(total=10)
        try:
            if method.upper() == "POST":
                async with self.session.post(
                    url, headers=headers, cookies=cookies, data=data or {}, proxy=proxy, timeout=timeout
                ) as resp:
                    text = await resp.text()
                    return json.loads(text)
            else:
                async with self.session.get(
                    url, headers=headers, cookies=cookies, proxy=proxy, timeout=timeout
                ) as resp:
                    text = await resp.text()
                    return json.loads(text)
        except Exception as e:
            logger.error(f"[NetEaseMusic] 请求失败: {e}")
            raise

    async def netease_search(self, keyword: str, limit: int = 5) -> List[dict]:
        """搜索网易云歌曲"""
        url = "http://music.163.com/api/search/get/web"
        data = {"s": keyword.strip(), "type": 1, "limit": limit, "offset": 0}
        
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                result = await self._netease_request(url, data=data, method="POST")
                
                if not isinstance(result, dict):
                    raise ValueError(f"意外的响应类型：{type(result)}")

                songs = result.get("result", {}).get("songs", [])
                if not isinstance(songs, list):
                    raise ValueError(f"“歌曲列表”并非一个列表")

                parsed_songs = []
                for song in songs[:limit]:
                    if not isinstance(song, dict):
                        continue
                    parsed_songs.append({
                        "id": song["id"],
                        "name": song["name"],
                        "artists": "、".join(artist["name"] for artist in song.get("artists", []) if isinstance(artist, dict) and "name" in artist),
                    })
                return parsed_songs

            except Exception as e:
                logger.warning(f"网易云搜索异常（第 {attempt + 1} 次）: {e}")
                if attempt < max_retries:
                    await asyncio.sleep(1)
                continue

        logger.error(f"网易云搜索最终失败，关键词: {keyword}")
        return []
    
    def _cancel_user_state(self, user_id: int):
        """取消用户的等待状态和定时器"""
        if user_id in USER_STATES:
            state = USER_STATES[user_id]
            if "timer" in state and state["timer"]:
                try:
                    state["timer"].cancel()
                except Exception:
                    pass
            del USER_STATES[user_id]

    def _on_selection_timeout(self, user_id: int):
        """处理选择超时 (回调函数)"""
        if user_id in USER_STATES:
            logger.info(f"用户 {user_id} 点歌选择超时，已清除状态。")
            self._cancel_user_state(user_id)

    async def _send_music_card(self, event: AiocqhttpMessageEvent, song_info: dict) -> dict:
        """发送音乐卡片"""
        if not self.is_qq_platform:
            msg = (
                f"🎵 找到了《{song_info['name']}》- {song_info['artists']}\n"
                "⚠️ 当前平台不支持直接播放网易云音乐。\n"
                "建议在 QQ 中使用本功能以获得最佳体验！"
            )
            await event.send(event.plain_result(msg))
            return {"ok": False, "error": "PlatformNotSupported", "detail": msg}

        song_id = str(song_info["id"])
        title = song_info["name"]
        artist = song_info["artists"]

        try:
            payload = {
                "message": [{
                    "type": "music",
                    "data": {"type": "163", "id": song_id}
                }]
            }
            
            if event.is_private_chat():
                payload["user_id"] = event.get_sender_id()
                await event.bot.call_action("send_private_msg", **payload)
            else:
                payload["group_id"] = event.get_group_id()
                await event.bot.call_action("send_group_msg", **payload)
            
            logger.info(f"已发送网易云卡片：{title} - {artist} (ID: {song_id})")
            
            response_msg = ""
            if self.play_success_message_template.strip():
                response_msg = self.play_success_message_template.format(title=title, artist=artist)
                await event.send(event.plain_result(response_msg))
            
            return {
                "ok": True, 
                "operation": "play_netease_song", 
                "song_id": song_id, 
                "title": title, 
                "artist": artist,
                "message": response_msg
            }

        except Exception as e:
            logger.error(f"发送音乐卡片失败：{e}")
            msg = "抱歉，发送音乐卡片失败了"
            await event.send(event.plain_result(msg))
            return {"ok": False, "error": "SendCardError", "detail": str(e)}

    @filter.llm_tool(name="play_netease_song_by_name")
    async def play_netease_song_by_name(
        self, event: AiocqhttpMessageEvent, song_name: str
    ) -> dict:
        """
        当用户想听歌时，根据歌名（可含歌手）搜索并播放网易云音乐。
        示例：
            1.用户说“我想听七里香”，LLM 调用此工具传入 song_name="七里香"
            2.用户说“播放周杰伦的晴天”，LLM 调用此工具传入 song_name="周杰伦 晴天"
        Args:
            song_name(string): 歌曲名称或包含歌手的关键词
        """

        if not song_name or not song_name.strip():
            msg = "歌名不能为空哦~"
            await event.send(event.plain_result(msg))
            return {"ok": False, "error": "ValidationError", "detail": msg}

        limit = self.search_limit if self.music_select else 1

        songs = await self.netease_search(song_name.strip(), limit=limit)

        if not songs:
            msg = f"没找到「{song_name}」相关的歌曲"
            await event.send(event.plain_result(msg))
            return {"ok": False, "error": "NotFoundError", "detail": msg}

        if self.music_select and len(songs) > 1:
            user_id = event.get_sender_id()
            
            self._cancel_user_state(user_id)

            msg_parts = [Plain(f"🔍 找到以下关于《{song_name}》的歌曲，请在 {self.select_wait_time}秒内 回复序号点歌：\n\n")]
            for idx, song in enumerate(songs, 1):
                msg_parts.append(Plain(f"{idx}. 《{song['name']}》 - {song['artists']}\n"))
            
            await event.send(event.chain_result(msg_parts))

            loop = asyncio.get_running_loop()
            timer = loop.call_later(self.select_wait_time, lambda: self._on_selection_timeout(user_id))
            
            USER_STATES[user_id] = {
                "state": "waiting_selection",
                "songs": songs,
                "timer": timer
            }
            
            return {
                "ok": True, 
                "detail": f"已找到 {len(songs)} 首歌曲，等待用户选择。",
                "mode": "selection"
            }
        else:
            first = songs[0]
            return await self._send_music_card(event, first)

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def handle_message_selection(self, event: AiocqhttpMessageEvent):
        user_id = event.get_sender_id()
        
        if user_id not in USER_STATES:
            return
        
        state = USER_STATES[user_id]
        if state.get("state") != "waiting_selection":
            return

        message_str = event.message_str.strip()
        
        if message_str.isdigit():
            idx = int(message_str)
            songs = state["songs"]
            
            if 1 <= idx <= len(songs):
                self._cancel_user_state(user_id) 
                
                selected_song = songs[idx - 1]
                
                try:
                    response_text = self.select_success_template.format(
                        index=idx,
                        title=selected_song['name'],
                        artist=selected_song['artists']
                    )
                except KeyError as e:
                    logger.warning(f"选歌成功模板变量缺失：{e}，使用默认文本")
                    response_text = f"好哒！这就为您播放第 {idx} 首：《{selected_song['name']}》"
                
                await event.send(event.plain_result(response_text))

                await self._send_music_card(event, selected_song)
            else:
                try:
                    response_text = self.select_error_template.format(
                        max_idx=len(songs)
                    )
                except KeyError as e:
                    logger.warning(f"选歌错误模板变量缺失：{e}，使用默认文本")
                    response_text = f"哎呀，序号只能在 1 到 {len(songs)} 之间哦~ 请重新输入。"
                    
                await event.send(event.plain_result(response_text))

        else:
            self._cancel_user_state(user_id)
            response_text = self.select_cancel_template
            await event.send(event.plain_result(response_text))