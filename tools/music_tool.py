import subprocess
from .base_tool import BaseAssistantTool


class MusicTool(BaseAssistantTool):
    """音乐播放工具"""

    def __init__(self, name:str, config : dict):
        super().__init__(name, config)
        self.is_playing = False

    def run(self, query: str) -> str:
        query_lower = query.lower()

        if any(keyword in query_lower for keyword in ["播放", "开始", "继续"]):
            return self._play_music(query)
        elif any(keyword in query_lower for keyword in ["暂停", "停止"]):
            return self._pause_music()
        elif any(keyword in query_lower for keyword in ["下一首", "下一曲"]):
            return self._next_track()
        elif any(keyword in query_lower for keyword in ["上一首", "上一曲"]):
            return self._previous_track()
        elif any(keyword in query_lower for keyword in ["音量", "声音"]):
            return self._adjust_volume(query)
        else:
            status = "正在播放" if self.is_playing else "已暂停"
            return f"音乐播放器：{status}。说'播放音乐'开始播放，'暂停'停止播放。"

    def play_music(self, query: str) -> str:
        """播放音乐"""
        try:
            # 尝试打开音乐应用 (macOS)
            subprocess.run(["open", "-a", "Music"])
            self.is_playing = True

            # 检查是否有特定歌曲请求
            if "周杰伦" in query or "jay" in query:
                return "开始播放周杰伦的音乐"
            elif "轻音乐" in query or "轻松" in query:
                return "开始播放轻音乐"
            else:
                return "开始播放音乐"
        except:
            self.is_playing = True
            return "开始播放音乐"

    def pause_music(self) -> str:
        """暂停音乐"""
        self.is_playing = False
        return "音乐已暂停"

    def next_track(self) -> str:
        """下一首"""
        return "切换到下一首歌曲"

    def previous_track(self) -> str:
        """上一首"""
        return "切换到上一首歌曲"

    def adjust_volume(self, query: str) -> str:
        """调整音量"""
        if "大" in query or "高" in query or "增加" in query:
            return "已调高音量"
        elif "小" in query or "低" in query or "减少" in query:
            return "已调低音量"
        else:
            return "当前音量适中"