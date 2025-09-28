import asyncio
import websockets
import json
import base64
import numpy as np
import whisper
import tempfile
import scipy.io.wavfile
from typing import Callable, Optional
from config import settings


class RealtimeAudioProcessor:
    """实时音频处理器"""

    def __init__(self):
        self.whisper_model = whisper.load_model(settings.WHISPER_MODEL)
        self.sample_rate = settings.REALTIME_AUDIO["sample_rate"]
        self.buffer_duration = settings.REALTIME_AUDIO["buffer_duration"]
        self.chunk_size = settings.REALTIME_AUDIO["chunk_size"]
        self.is_listening = False
        self.audio_buffer = []
        self.callback: Optional[Callable] = None
        self.websocket = None

    async def start_listening(self, websocket, callback: Callable):
        """开始监听音频流"""
        self.is_listening = True
        self.callback = callback
        self.websocket = websocket
        self.audio_buffer = []

        print("开始实时语音采集...")

        try:
            async for message in websocket:
                if not self.is_listening:
                    break

                # 处理音频数据
                await self._process_audio_message(message)
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket连接已关闭")
        except Exception as e:
            print(f"音频处理错误: {e}")
        finally:
            self.is_listening = False

    async def _process_audio_message(self, message):
        """处理音频消息"""
        try:
            data = json.loads(message)

            if data.get("type") == "audio":
                # 解码Base64音频数据
                audio_data = base64.b64decode(data["data"])

                # 转换为numpy数组
                audio_array = np.frombuffer(audio_data, dtype=np.int16)

                # 添加到缓冲区
                self.audio_buffer.extend(audio_array)

                # 检查缓冲区是否达到处理长度
                buffer_length = len(self.audio_buffer) / self.sample_rate
                if buffer_length >= self.buffer_duration:
                    await self._process_buffer()

            elif data.get("type") == "stop":
                # 处理剩余缓冲区
                if self.audio_buffer:
                    await self._process_buffer()
                self.is_listening = False

        except Exception as e:
            print(f"处理音频消息错误: {e}")

    async def _process_buffer(self):
        """处理音频缓冲区"""
        if not self.audio_buffer:
            return

        try:
            # 转换为numpy数组
            audio_array = np.array(self.audio_buffer, dtype=np.int16)

            # 保存为临时文件进行识别
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                scipy.io.wavfile.write(temp_file.name, self.sample_rate, audio_array)

                # 语音识别
                result = self.whisper_model.transcribe(
                    temp_file.name,
                    fp16=False,
                    language="zh"
                )

                text = result["text"].strip()
                if text:
                    print(f"识别结果: {text}")

                    # 调用回调函数处理文本
                    if self.callback:
                        response = await self.callback(text)

                        # 发送响应回客户端
                        if self.websocket:
                            await self._send_response(response)

            # 清空缓冲区（保留最后0.5秒数据用于上下文）
            keep_samples = int(0.5 * self.sample_rate)
            self.audio_buffer = self.audio_buffer[-keep_samples:] if len(self.audio_buffer) > keep_samples else []

        except Exception as e:
            print(f"处理音频缓冲区错误: {e}")
            self.audio_buffer = []

    async def _send_response(self, response_text: str):
        """发送响应到客户端"""
        try:
            response_data = {
                "type": "response",
                "text": response_text,
                "timestamp": asyncio.get_event_loop().time()
            }
            await self.websocket.send(json.dumps(response_data))
        except Exception as e:
            print(f"发送响应错误: {e}")

    def stop_listening(self):
        """停止监听"""
        self.is_listening = False


class AudioStreamManager:
    """音频流管理器"""

    def __init__(self):
        self.active_connections = {}
        self.audio_processors = {}

    async def handle_connection(self, websocket, path):
        """处理WebSocket连接"""
        connection_id = id(websocket)
        print(f"新的音频连接: {connection_id}")

        # 创建音频处理器
        audio_processor = RealtimeAudioProcessor()
        audio_processor.websocket = websocket

        # 存储连接和处理器
        self.active_connections[connection_id] = websocket
        self.audio_processors[connection_id] = audio_processor

        try:
            # 开始处理音频流
            await audio_processor.start_listening(
                websocket,
                self._handle_recognized_text
            )
        except Exception as e:
            print(f"处理连接错误: {e}")
        finally:
            # 清理资源
            if connection_id in self.active_connections:
                del self.active_connections[connection_id]
            if connection_id in self.audio_processors:
                del self.audio_processors[connection_id]
            print(f"连接关闭: {connection_id}")

    async def _handle_recognized_text(self, text: str) -> str:
        """处理识别到的文本"""
        # 这里可以集成现有的语音助手逻辑
        # 暂时返回简单响应
        if "天气" in text:
            return "今天天气晴朗，气温25度，适宜外出。"
        elif "时间" in text:
            import datetime
            return f"现在是{datetime.datetime.now().strftime('%H:%M')}"
        else:
            return f"您说: {text}。我听到了，但需要更多上下文来回答。"

    async def broadcast_message(self, message: str):
        """广播消息到所有连接"""
        disconnected = []
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send(json.dumps({
                    "type": "notification",
                    "message": message
                }))
            except websockets.exceptions.ConnectionClosed:
                disconnected.append(connection_id)

        # 清理断开的连接
        for connection_id in disconnected:
            if connection_id in self.active_connections:
                del self.active_connections[connection_id]
            if connection_id in self.audio_processors:
                del self.audio_processors[connection_id]


class AssistantAudioManager(AudioStreamManager):
    """集成语音助手的音频管理器"""

    def __init__(self, assistant):
        super().__init__()
        self.assistant = assistant

    async def _handle_recognized_text(self, text: str) -> str:
        """使用语音助手处理识别到的文本"""
        try:
            # 使用语音助手处理文本
            response = self.assistant.process_text(text)
            print(f"助手响应: {response}")
            return response
        except Exception as e:
            print(f"处理文本错误: {e}")
            return "抱歉，我暂时无法处理这个请求"