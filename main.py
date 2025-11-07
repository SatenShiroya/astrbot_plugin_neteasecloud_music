import json
import aiohttp
from astrbot.api.event import filter
from astrbot.core.message.message_event_result import MessageEventResult
from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import AiocqhttpMessageEvent
from astrbot.api.star import Star, register, Context
from astrbot.api import logger


@register("astrbot_plugin_NetEaseCloud_Music", "SatenShiroya", "网易云音乐点歌插件：支持 LLM 自动点歌", "1.0.0")
class MusicPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.session = None  # 初始化为 None

    async def initialize(self):
        """插件初始化：创建 aiohttp 会话"""
        self.session = aiohttp.ClientSession()

    async def _netease_request(self, url: str, data: dict = None, method: str = "GET"):
        """网易云统一请求方法"""
        headers_post = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/55.0.2883.87 UBrowser/6.2.4098.3 Safari/537.36"
        }
        headers_get = {"referer": "http://music.163.com"}
        cookies = {"appver": "2.0.2"}

        if method.upper() == "POST":
            async with self.session.post(
                url, headers=headers_post, cookies=cookies, data=data or {}
            ) as resp:
                ct = resp.headers.get("Content-Type", "")
                if "application/json" in ct:
                    return await resp.json()
                else:
                    return json.loads(await resp.text())
        else:
            async with self.session.get(url, headers=headers_get, cookies=cookies) as resp:
                return await resp.json()

    async def netease_search(self, keyword: str, limit: int = 5) -> list[dict]:
        """搜索网易云歌曲"""
        url = "http://music.163.com/api/search/get/web"
        data = {"s": keyword.strip(), "type": 1, "limit": limit, "offset": 0}
        try:
            result = await self._netease_request(url, data=data, method="POST")
            songs = result.get("result", {}).get("songs", [])
            return [
                {
                    "id": song["id"],
                    "name": song["name"],
                    "artists": "、".join(artist["name"] for artist in song["artists"]),
                }
                for song in songs[:limit]
            ]
        except Exception as e:
            logger.error(f"网易云搜索失败: {e}")
            return []

    async def netease_fetch_extra(self, song_id: str | int) -> dict[str, str]:
        """获取音频链接（用于非 QQ 平台兜底）"""
        url = f"https://www.hhlqilongzhu.cn/api/dg_wyymusic.php?id={song_id}&br=7&type=json"
        try:
            result = await self._netease_request(url)
            return {
                "title": result.get("title", "未知"),
                "author": result.get("singer", "未知"),
                "audio_url": result.get("music_url", ""),
            }
        except Exception as e:
            logger.error(f"获取音频链接失败 (ID={song_id}): {e}")
            return {"audio_url": ""}

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
            yield event.plain_result("歌名不能为空哦~")
            return

        songs = await self.netease_search(song_name.strip())
        if not songs:
            yield event.plain_result(f"没找到「{song_name}」相关的歌曲 ")
            return

        first = songs[0]
        song_id = str(first["id"])
        title = first["name"]
        artist = first["artists"]

        # QQ 平台：发送音乐卡片
        if isinstance(event, AiocqhttpMessageEvent):
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

                logger.info(f"已发送网易云卡片: {title} - {artist} (ID: {song_id})")
                yield event.plain_result(f"🎵 已为你播放《{title}》")
                return
            except Exception as e:
                logger.error(f"发送音乐卡片失败: {e}")
                yield event.plain_result("抱歉，发送音乐卡片失败了")
                return

        # 其他平台：发音频链接
        extra = await self.netease_fetch_extra(song_id)
        audio_url = extra.get("audio_url")
        if audio_url:
            yield event.plain_result(f"🎶 {title} - {artist}\n🔗 {audio_url}")
            return
        else:
            yield event.plain_result(f"找到了歌曲《{title}》，但无法获取播放链接。")
            return
    
    async def terminate(self):
        """插件销毁：关闭会话"""
        if self.session:
            await self.session.close()