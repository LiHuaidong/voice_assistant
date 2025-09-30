from typing import Optional, Any
import re
from external_services.amap_service import getLocation, getWeatherInfo
from tools.base_tool import BaseAssistantTool

class WeatherTool(BaseAssistantTool):
    """天气查询工具"""

    def __init__(self, name:str, config : dict):
        super().__init__(name, config)

    def run(self, query: str) -> str | None:
        # 提取城市名称
        city = self.extract_city(query)

        if not city:
            # 尝试获取当前位置
            current_city = self.get_current_city()
            if current_city:
                city = current_city
            else:
                return "无法确定您的位置，请明确指定要查询的城市"

        return self.get_weather_data(city)

    def extract_city(self, query : str) -> str | None | Any:
        """从查询中提取城市名称"""
        cities = ['北京', '上海', '广州', '深圳', '杭州', '南京', '成都', '武汉',
                  '西安', '重庆', '天津', '苏州', '郑州', '长沙', '沈阳', '青岛',
                  '大连', '宁波', '厦门', '福州', '无锡', '合肥', '太原', '南昌',
                  '石家庄', '哈尔滨', '长春', '兰州', '银川', '西宁', '乌鲁木齐',
                  '拉萨', '南宁', '贵阳', '昆明', '海口', '香港', '澳门', '台北']

        for city in cities:
            if city in query:
                return city

        # 尝试匹配模式
        patterns = [
            r'([\u4e00-\u9fa5]{2,4}?)市.*天气',
            r'([\u4e00-\u9fa5]{2,4}?)天气',
            r'天气.*([\u4e00-\u9fa5]{2,4}?)市',
            r'查询.*([\u4e00-\u9fa5]{2,4}?)的天气'
        ]
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                return match.group(1)

        return None

    def get_current_city(self) -> Optional[str]:
        """获取当前城市"""
        return getLocation()

    def get_weather_data(self, city: str) -> str:
        """获取天气数据"""
        return getWeatherInfo(city)

if __name__ == '__main__':
    config = {
        "name": "weather_tool",
        "description": "查询指定城市的天气信息。如果不指定城市，会自动获取当前位置的天气。",
        "class_path": "tools.weather_tool.WeatherTool",
        "enabled": True,
        "config": {
          "api_key": "YOUR_AMAP_API_KEY",
          "timeout": 10,
          "base_url": "https://restapi.amap.com/v3"
        }
      }
    weatherTool = WeatherTool("weather_tool", config)
    weatherTool.run("查询深圳的天气")