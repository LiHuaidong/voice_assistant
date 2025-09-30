import os
from pathlib import Path
from dotenv import load_dotenv

class Settings:
    """应用配置类"""

    # 语音识别设置
    SAMPLE_RATE = 16000
    RECORD_DURATION = 5  # 录音时长（秒）

    # 语音合成设置
    TTS_RATE = 160

    # 模型设置
    WHISPER_MODEL = "base"
    LLM_MODEL = "deepseek-r1:14b"

    # 服务地址
    MCP_WEATHER_URL = "http://localhost:5000/mcp/tools/weather_tool/execute"
    OLLAMA_URL = "http://localhost:11434/api/generate"

    # 工具配置
    TOOL_CONFIG = {
        "weather": {
            "enabled": True,
            "timeout": 10
        },
        "calendar": {
            "enabled": True
        },
        "files": {
            "enabled": True
        },
        "music": {
            "enabled": True
        },
        "system": {
            "enabled": True
        },
        "calculator": {
            "enabled": True
        }
    }
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)  # 加载.env文件中的环境变量到os.environ中

    # WebSocket 配置
    WEBSOCKET_HOST = os.getenv("WEBSOCKET_HOST", "localhost")
    WEBSOCKET_PORT = int(os.getenv("WEBSOCKET_PORT", 8765))

    # 实时音频配置
    REALTIME_AUDIO = {
        "sample_rate": 16000,
        "buffer_duration": 2.0,  # 缓冲区时长（秒）
        "chunk_size": 1024,  # 音频块大小
        "silence_threshold": 500,  # 静音阈值
        "max_silence_duration": 3.0  # 最大静音时长（秒）
    }

    # LangSmith 配置
    LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
    LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "voice-assistant")

    # LangServe 配置
    LANGSERVE_HOST = os.getenv("LANGSERVE_HOST", "0.0.0.0")
    LANGSERVE_PORT = int(os.getenv("LANGSERVE_PORT", 8000))

    # LangChain 详细日志配置
    LANGCHAIN_VERBOSE = os.getenv("LANGCHAIN_VERBOSE", "false").lower() == "true"

    # 高德地图配置
    AMAP_API_KEY = os.getenv("AMAP_API_KEY")
    IP_LOCATION_API = os.getenv("IP_LOCATION_API", 'https://restapi.amap.com/v3/ip')
    WEATHER_INFO_API = os.getenv("WEATHER_INFO_API", 'https://restapi.amap.com/v3/weather/weatherInfo')

settings = Settings()
print(settings.WEBSOCKET_HOST)
