#!/usr/bin/env python
"""
语音助手主程序入口
支持语音模式、文本模式和工具管理
"""

import sys
import os
import asyncio
import websockets
from core.tool_registry import tool_registry

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.assistant import VoiceAssistant


class TextModeAssistant:
    """文本模式助手"""

    def __init__(self, assistant):
        self.assistant = assistant

    async def run(self):
        """运行文本模式"""
        print("语音助手已启动（文本模式）")
        print("输入'退出'或'quit'结束程序")
        print("支持的功能：", ", ".join(self.assistant.agent.tools.keys()))

        while True:
            try:
                user_input = input("\n你说：").strip()

                if user_input.lower() in ['退出', 'quit', 'exit', 'q']:
                    print("再见！")
                    break

                if not user_input:
                    continue

                # 处理用户输入
                response = await self.assistant.process_text(user_input)
                print(f"助手：{response}")

                # 语音播报
                self.assistant.text_to_speech(response)

            except KeyboardInterrupt:
                print("\n再见！")
                break
            except Exception as e:
                print(f"错误: {e}")


class ToolManagementMode:
    """工具管理模式"""

    def __init__(self, assistant: VoiceAssistant):
        self.assistant = assistant

    def run(self):
        """运行工具管理模式"""
        print("工具管理控制台")
        print("可用命令: list, add, remove, reload, exit")

        while True:
            try:
                command = input("\n工具管理> ").strip().lower()

                if command in ['exit', 'quit', 'q']:
                    break

                if command == 'list':
                    self._list_tools()
                elif command == 'add':
                    self._add_tool()
                elif command == 'remove':
                    self._remove_tool()
                elif command == 'reload':
                    self._reload_tools()
                else:
                    print("未知命令，可用命令: list, add, remove, reload, exit")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"错误: {e}")

    def _list_tools(self):
        """列出所有工具"""
        tools = self.assistant.agent.tools
        print("\n已注册工具:")
        for name, tool in tools.items():
            print(f"- {name}: {tool.description}")

        active_tools = tool_registry.get_all_tools()
        print("\n已启用工具:")
        for name in active_tools:
            print(f"- {name}")

    def _add_tool(self):
        """添加新工具"""
        print("\n添加新工具")
        name = input("工具名称: ").strip()
        class_path = input("工具类路径 (例如 tools.calculator_tool.CalculatorTool): ").strip()

        # 配置参数
        config = {}
        print("输入配置参数 (键=值, 空行结束):")
        while True:
            line = input("> ").strip()
            if not line:
                break
            if '=' not in line:
                print("格式错误，应为 键=值")
                continue
            key, value = line.split('=', 1)
            config[key.strip()] = value.strip()

        enable = input("是否启用? (y/n): ").strip().lower() == 'y'

        self.assistant.add_tool(name, class_path, config, enable)
        print(f"工具 '{name}' 已添加")

    def _remove_tool(self):
        """移除工具"""
        name = input("要移除的工具名称: ").strip()
        self.assistant.remove_tool(name)

    def _reload_tools(self):
        """重新加载工具配置"""
        self.assistant.reload_tools()
        print("工具配置已重新加载")


async def main():
    """主函数"""
    print("=" * 50)
    print("          智能语音助手 - 支持动态语音采集")
    print("=" * 50)

    # 创建助手实例
    assistant = VoiceAssistant()

    # 选择运行模式
    print("\n请选择运行模式:")
    print("1. 语音模式（需要麦克风）")
    print("2. 文本模式（手动输入）")
    print("3. 工具管理模式")
    print("4. 启动 WebSocket 语音服务")
    print("5. 启动 LangServe API 服务")

    try:
        choice = input("请输入选择 (1, 2, 3, 4 或 5): ").strip()

        if choice == "1":
            await assistant.run_voice_mode()  # 正确等待异步函数
        elif choice == "2":
            text_assistant = TextModeAssistant(assistant)
            await text_assistant.run()  # 正确等待异步函数
        elif choice == "3":
            tool_manager = ToolManagementMode(assistant)
            tool_manager.run()
        elif choice == "4":
            # 启动 WebSocket 服务
            import subprocess
            subprocess.run(["python", "websocket_server.py"])
        elif choice == "5":
            # 启动 LangServe 服务
            import subprocess
            subprocess.run(["python", "serve.py"])
        else:
            print("无效选择")
    except Exception as e:
        print(f"程序出错: {e}")


if __name__ == "__main__":
    # 使用 asyncio.run() 运行主函数
    asyncio.run(main())