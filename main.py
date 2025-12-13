import json
import aiohttp
from astrbot.api.event import filter
from astrbot.core.message.message_event_result import MessageEventResult
from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import AiocqhttpMessageEvent
from astrbot.api.star import Star, register, Context
from astrbot.api import logger, AstrBotConfig


@register("astrbot_plugin_NetEaseCloud_Music", "SatenShiroya", "网易云音乐点歌插件：支持 LLM 自动点歌", "1.3.0")
class MusicPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.session = None

        self.play_success_message_template = config.get("play_success_message_template","🎵已为您播放《{title}》")

        self.proxy_url = config.get("proxy_url", "")

    async def initialize(self):
        """初始化 aiohttp ClientSession，根据代理类型创建连接器"""
        connector = None

        if self.proxy_url.startswith(("socks4://", "socks5://")):
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

    async def _netease_request(self, url: str, data: dict = None, method: str = "GET"):
        """统一请求方法，自动应用代理（如配置）"""
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
                    url,
                    headers=headers,
                    cookies=cookies,
                    data=data or {},
                    proxy=proxy,
                    timeout=timeout,
                ) as resp:
                    text = await resp.text()
                    return json.loads(text)
            else:
                async with self.session.get(
                    url,
                    headers=headers,
                    cookies=cookies,
                    proxy=proxy,
                    timeout=timeout,
                ) as resp:
                    text = await resp.text()
                    return json.loads(text)
        except Exception as e:
            logger.error(f"[NetEaseMusic] 请求失败 (URL: {url}, 代理: {proxy}): {e}")
            raise

    async def netease_search(self, keyword: str, limit: int = 5) -> list[dict]:
        """搜索网易云歌曲（带重试）"""

        url = "http://music.163.com/api/search/get/web"
        data = {"s": keyword.strip(), "type": 1, "limit": limit, "offset": 0}
        
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                result = await self._netease_request(url, data=data, method="POST")
                
                # 确保 result 是 dict
                if not isinstance(result, dict):
                    raise ValueError(f"意外的响应类型： {type(result)}")

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

            except (json.JSONDecodeError, ValueError, KeyError, TypeError) as e:
                logger.warning(f"网易云搜索解析失败（第 {attempt + 1} 次）: {e}")
            except Exception as e:
                logger.warning(f"网易云搜索请求异常（第 {attempt + 1} 次）: {e}")

            if attempt < max_retries:
                continue

        logger.error(f"网易云搜索最终失败，关键词: {keyword}")
        return []

    @filter.llm_tool(name="play_netease_song_by_name")
    async def play_netease_song_by_name(
        self, event: AiocqhttpMessageEvent, song_name: str
    ) -> MessageEventResult:
        """
        当用户想听歌时，根据歌名（可含歌手）搜索并播放网易云音乐。
        示例：
            1.用户说“我想听七里香”，LLM 调用此工具传入 song_name="七里香"
            2.用户说“播放周杰伦的晴天”，LLM 调用此工具传入 song_name="周杰伦 晴天"
        Args:
            song_name(string): 歌曲名称或包含歌手的关键词
        """
        if not song_name or not song_name.strip():
            yield event.plain_result(f"歌名不能为空哦~")
            return

        songs = await self.netease_search(song_name.strip())
        if not songs:
            yield event.plain_result(f"没找到「{song_name}」相关的歌曲 ")
            return

        first = songs[0]
        song_id = str(first["id"])
        title = first["name"]
        artist = first["artists"]

        # 非 QQ 平台：发送文本提示
        if not isinstance(event, AiocqhttpMessageEvent):
            yield event.plain_result(
                f"🎵 找到了《{title}》- {artist}\n"
                "⚠️ 当前平台不支持直接播放网易云音乐。\n"
                "建议在 QQ 中使用本功能以获得最佳体验！"
            )
            return

        # QQ 平台：发送音乐卡片
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
            
            template = self.play_success_message_template
            logger.info(f"已发送网易云卡片: {title} - {artist} (ID: {song_id})")
            if template.strip():
                message = template.format(title=title, artist=artist)
                yield event.plain_result(f"{message}")
            return
        except Exception as e:
            logger.error(f"发送音乐卡片失败: {e}")
            yield event.plain_result(f"抱歉，发送音乐卡片失败了")
            return

    async def terminate(self):
        """插件销毁：关闭 aiohttp 会话"""
        if self.session:
            await self.session.close()