import subprocess
from .base_tool import BaseAssistantTool
from datetime import datetime


class SystemTool(BaseAssistantTool):
    """系统控制工具"""

    def __init__(self, name:str, config : dict):
        super().__init__(name, config)

    def run(self, query: str) -> str:
        query_lower = query.lower()

        if any(keyword in query_lower for keyword in ["锁屏", "锁定"]):
            return self._lock_screen()
        elif any(keyword in query_lower for keyword in ["关机", "关闭", "睡眠"]):
            return "出于安全考虑，请手动执行关机操作。"
        elif any(keyword in query_lower for keyword in ["应用", "程序", "打开"]):
            return self._open_application(query)
        elif any(keyword in query_lower for keyword in ["时间", "几点"]):
            return self._get_time()
        else:
            return "我可以帮您锁屏、打开应用程序或查看时间，请明确您的需求。"

    def lock_screen(self) -> str:
        """锁屏"""
        try:
            # macOS
            subprocess.run(["pmset", "displaysleepnow"])
            return "屏幕已锁定"
        except:
            return "锁屏功能当前不可用"

    def open_application(self, query: str) -> str:
        """打开应用程序"""
        apps = {
            "浏览器": "Safari",
            "邮件": "Mail",
            "音乐": "Music",
            "日历": "Calendar",
            "终端": "Terminal",
            "计算器": "Calculator",
            "备忘录": "Notes",
            "照片": "Photos",
            "信息": "Messages",
            "设置": "System Preferences"
        }

        for keyword, app_name in apps.items():
            if keyword in query:
                try:
                    subprocess.run(["open", "-a", app_name])
                    return f"已打开 {app_name}"
                except:
                    return f"无法打开 {app_name}"

        return "请指定要打开的应用程序名称"

    def get_time(self) -> str:
        """获取当前时间"""
        now = datetime.now()
        return f"现在是 {now.strftime('%Y年%m月%d日 %H:%M:%S')}"