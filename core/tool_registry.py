import importlib
import json
import os
from typing import Dict, Type, Any
from tools.base_tool import BaseAssistantTool
from config import settings


class ToolRegistry:
    """工具注册与管理类"""

    _instance = None
    _tools: Dict[str, Type[BaseAssistantTool]] = {}
    _active_tools: Dict[str, BaseAssistantTool] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ToolRegistry, cls).__new__(cls)
            cls._instance._load_tool_config()
        return cls._instance

    def _load_tool_config(self):
        """从配置文件加载工具配置"""
        config_path = os.path.join(os.path.dirname(__file__), '../config/tools_config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                tool_configs = json.load(f)

            for tool_config in tool_configs:
                self.register_tool(
                    tool_config["name"],
                    tool_config["class_path"],
                    enabled=tool_config.get("enabled", True),
                    config=tool_config.get("config", {})
                )
        except Exception as e:
            print(f"加载工具配置失败: {str(e)}")
            # 默认加载核心工具
            self._load_default_tools()

    def _load_default_tools(self):
        """加载默认工具集"""
        default_tools = [
            {
                "name": "weather_tool",
                "class_path": "tools.weather_tool.WeatherTool",
                "enabled": True
            },
            {
                "name": "calendar_tool",
                "class_path": "tools.calendar_tool.CalendarTool",
                "enabled": True
            },
            {
                "name": "file_tool",
                "class_path": "tools.file_tool.FileTool",
                "enabled": True
            },
            {
                "name": "music_tool",
                "class_path": "tools.music_tool.MusicTool",
                "enabled": True
            },
            {
                "name": "system_tool",
                "class_path": "tools.system_tool.SystemTool",
                "enabled": True
            },
            {
                "name": "calculator_tool",
                "class_path": "tools.calculator_tool.CalculatorTool",
                "enabled": True
            }
        ]

        for tool_config in default_tools:
            self.register_tool(
                tool_config["name"],
                tool_config["class_path"],
                enabled=tool_config.get("enabled", True)
            )

    def register_tool(self, name: str, class_path: str, enabled: bool = True, config: Dict[str, Any] = None):
        """注册工具类"""
        if name in self._tools:
            print(f"警告: 工具 '{name}' 已注册，将被覆盖")

        try:
            # 动态导入工具类
            module_name, class_name = class_path.rsplit('.', 1)
            module = importlib.import_module(module_name)
            tool_class = getattr(module, class_name)

            if not issubclass(tool_class, BaseAssistantTool):
                raise TypeError(f"注册的工具类必须继承自 BaseAssistantTool: {class_path}")

            self._tools[name] = tool_class

            # 如果启用，则创建实例
            if enabled:
                self._active_tools[name] = tool_class(name=name, config=config or {})
                print(f"工具 '{name}' 已注册并启用")
            else:
                print(f"工具 '{name}' 已注册但未启用")

        except Exception as e:
            print(f"注册工具 '{name}' 失败: {str(e)}")

    def unregister_tool(self, name: str):
        """取消注册工具"""
        if name in self._tools:
            del self._tools[name]
            if name in self._active_tools:
                del self._active_tools[name]
            print(f"工具 '{name}' 已取消注册")
        else:
            print(f"警告: 尝试取消注册未注册的工具 '{name}'")

    def enable_tool(self, name: str):
        """启用工具"""
        if name in self._tools:
            if name not in self._active_tools:
                tool_class = self._tools[name]
                self._active_tools[name] = tool_class()
                print(f"工具 '{name}' 已启用")
            else:
                print(f"工具 '{name}' 已经启用")
        else:
            print(f"警告: 尝试启用未注册的工具 '{name}'")

    def disable_tool(self, name: str):
        """禁用工具"""
        if name in self._active_tools:
            del self._active_tools[name]
            print(f"工具 '{name}' 已禁用")
        else:
            print(f"警告: 尝试禁用未启用的工具 '{name}'")

    def get_tool(self, name: str) -> BaseAssistantTool:
        """获取工具实例"""
        return self._active_tools.get(name)

    def get_all_tools(self) -> Dict[str, BaseAssistantTool]:
        """获取所有启用的工具"""
        return self._active_tools

    def reload_config(self):
        """重新加载工具配置"""
        self._active_tools.clear()
        self._load_tool_config()

    def add_dynamic_tool(self, name: str, class_path: str, config: Dict[str, Any] = None, enable: bool = True):
        """动态添加新工具"""
        self.register_tool(name, class_path, enabled=enable, config=config)
        # 更新配置文件
        self._update_config_file(name, class_path, config, enable)

    def _update_config_file(self, name: str, class_path: str, config: Dict[str, Any], enabled: bool):
        """更新工具配置文件"""
        config_path = os.path.join(os.path.dirname(__file__), '../../config/tools_config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                tool_configs = json.load(f)

            # 检查是否已存在
            existing = next((t for t in tool_configs if t["name"] == name), None)

            if existing:
                # 更新现有配置
                existing["class_path"] = class_path
                existing["config"] = config
                existing["enabled"] = enabled
            else:
                # 添加新配置
                tool_configs.append({
                    "name": name,
                    "class_path": class_path,
                    "enabled": enabled,
                    "config": config or {}
                })

            # 写回文件
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(tool_configs, f, indent=2, ensure_ascii=False)

            print(f"工具 '{name}' 配置已更新")
        except Exception as e:
            print(f"更新工具配置文件失败: {str(e)}")


# 全局工具注册表实例
tool_registry = ToolRegistry()