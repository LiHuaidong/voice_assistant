import json
from datetime import datetime

import requests

from config.settings import settings


def getLocation() -> str:
    url = "{}?key={}".format(settings.IP_LOCATION_API, settings.AMAP_API_KEY)
    response = requests.get(url)
    if response is None or response.status_code != 200:
        return ""

    result = json.loads(response.text)
    return result['adcode']


def getWeatherInfo(city_or_adcode: str) -> str:
    url = "{}?key={}&city={}".format(settings.WEATHER_INFO_API, settings.AMAP_API_KEY, city_or_adcode)

    try:
        response = requests.get(url)
        if response is None or response.status_code != 200:
            return "天气服务暂时不可用"
        else:
            result = json.loads(response.text)
            return generate_weather_report(result['lives'][0])
    except Exception as e:
        return f"获取天气信息失败: {str(e)}"


def generate_weather_report(data):
    """
    将天气字典数据转换为自然语言播报文本
    :param data: 天气数据字典
    :return: 格式化后的天气播报文本
    """
    try:
        # 解析时间
        report_time = datetime.strptime(data['reporttime'], '%Y-%m-%d %H:%M:%S')
        weekday = "星期" + ["一", "二", "三", "四", "五", "六", "日"][report_time.weekday()]

        # 构建播报文本
        report = (
            f"现在是{report_time.year}年{report_time.month}月{report_time.day}日"
            f"{weekday}{report_time.hour:02d}:{report_time.minute:02d}分，"
            f"{data['province']}{data['city']}当前天气为{data['weather']}，"
            f"气温{data['temperature']}℃，湿度{data['humidity']}%，"
            f"风向为{data['winddirection']}风，风力等级{data['windpower']}。"
        )

        return report

    except (KeyError, ValueError) as e:
        return f"天气数据解析失败: {str(e)}"


# if __name__ == '__main__':
#     from pathlib import Path
#     from dotenv import load_dotenv
#     env_path = Path('..') / '.env'
#     load_dotenv(dotenv_path=env_path)
#     print(getWeatherInfo("广州"))

if __name__ == "__main__":
    example_data = {
        "adcode": "440300",
        "city": "深圳市",
        "humidity": "80",
        "province": "广东",
        "reporttime": "2025-09-28 23:30:38",
        "temperature": "27",
        "weather": "阴",
        "winddirection": "东",
        "windpower": "≤3"
    }

    print(generate_weather_report(example_data))
