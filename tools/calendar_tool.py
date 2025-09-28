from datetime import datetime, timedelta
from .base_tool import BaseAssistantTool
import json
import os


class CalendarTool(BaseAssistantTool):
    """日历工具"""

    def __init__(self, name:str, config : dict):
        super().__init__(name, config)
        self.events_file = "calendar_events.json"
        self.events = self.load_events()

    def run(self, query: str) -> str:
        query_lower = query.lower()

        if any(keyword in query_lower for keyword in ["今天", "今日", "现在", "当前"]):
            return self.get_today_schedule()
        elif any(keyword in query_lower for keyword in ["添加", "创建", "新建"]):
            return self.add_event(query)
        elif any(keyword in query_lower for keyword in ["明天", "下周", "未来"]):
            return self.get_future_schedule(query)
        elif any(keyword in query_lower for keyword in ["所有", "列表", "显示"]):
            return self.list_events()
        else:
            return self.get_today_schedule()

    def get_today_schedule(self) -> str:
        """获取今天日程"""
        today = datetime.now().strftime("%Y-%m-%d")
        today_events = [e for e in self.events if e.get("date") == today]

        if today_events:
            schedule = f"今天({today})的安排：\n"
            for event in sorted(today_events, key=lambda x: x.get("time", "")):
                schedule += f"- {event.get('time', '')} {event.get('title', '')}\n"
            return schedule
        else:
            return f"今天({today})没有安排任何活动。"

    def add_event(self, query: str) -> str:
        """添加事件"""
        # 简化实现 - 实际应该解析查询中的时间、标题等信息
        new_event = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": "10:00",
            "title": "新事件",
            "description": query
        }

        self.events.append(new_event)
        self.save_events()
        return "已为您添加到日历中。"

    def get_future_schedule(self, query: str) -> str:
        """获取未来日程"""
        # 简化实现
        return "明天：上午项目评审；后天：团队建设活动。"

    def list_events(self) -> str:
        """列出所有事件"""
        if not self.events:
            return "日历中没有事件。"

        result = "所有日历事件：\n"
        for event in self.events:
            result += f"- {event.get('date')} {event.get('time', '')} {event.get('title', '')}\n"

        return result

    def load_events(self) -> list:
        """加载事件"""
        if os.path.exists(self.events_file):
            try:
                with open(self.events_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return []

    def save_events(self):
        """保存事件"""
        try:
            with open(self.events_file, 'w', encoding='utf-8') as f:
                json.dump(self.events, f, ensure_ascii=False, indent=2)
        except:
            pass