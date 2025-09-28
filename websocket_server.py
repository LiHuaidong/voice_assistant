#!/usr/bin/env python
"""
WebSocket 实时语音服务入口
支持动态语音采集和实时交互
"""

import asyncio
import websockets
import json
import logging
from core.assistant import VoiceAssistant
from config import settings

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("websocket_server")


class VoiceWebSocketServer:
    """语音WebSocket服务器"""

    def __init__(self):
        self.assistant = VoiceAssistant()
        self.port = settings.WEBSOCKET_PORT

    async def handle_websocket(self, websocket, path):
        """处理WebSocket连接"""
        logger.info(f"新的WebSocket连接: {path}")
        await self.assistant.start_realtime_mode(websocket)

    async def start_server(self):
        """启动WebSocket服务器"""
        logger.info(f"启动WebSocket服务器，端口: {self.port}")

        server = await websockets.serve(
            self.handle_websocket,
            settings.WEBSOCKET_HOST,
            self.port
        )

        logger.info("WebSocket服务器已启动")

        try:
            # 保持服务器运行
            await asyncio.Future()
        except KeyboardInterrupt:
            logger.info("收到中断信号，关闭服务器")
        finally:
            server.close()
            await server.wait_closed()
            logger.info("WebSocket服务器已关闭")


if __name__ == "__main__":
    server = VoiceWebSocketServer()
    asyncio.run(server.start_server())