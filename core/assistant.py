from langgraph.graph import StateGraph, END
from typing import Dict, Any, TypedDict, Optional
import pyttsx3
import asyncio
import os
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool as LangchainTool
from langchain.memory import ConversationBufferWindowMemory
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.callbacks.manager import tracing_v2_enabled

from .speech_utils import SpeechUtils
from .tool_registry import tool_registry
from .realtime_audio import AssistantAudioManager
from .langsmith_integration import langsmith_integration
from config.settings import settings


# 定义状态数据结构
class AssistantState(TypedDict):
    audio_path: Optional[str]
    recognized_text: Optional[str]
    intent: Optional[str]
    tool_result: Optional[str]
    response_text: Optional[str]
    synthesis_complete: bool


class VoiceAssistant:
    """语音助手核心类（修复 tracing_v2_enabled 参数问题）"""

    def __init__(self):
        # 初始化语音组件
        self.speech_utils = SpeechUtils()
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', settings.TTS_RATE)

        # 初始化LLM
        self.llm = OllamaLLM(model=settings.LLM_MODEL, temperature=0.7)

        # 创建工具集
        self.tools = self._get_langchain_tools()

        # 创建内存
        self.memory = self._create_memory()

        # 创建智能体
        self.agent = self._create_agent()

        # 创建工作流
        self.workflow = self._create_workflow()

        # 实时音频管理器
        self.audio_manager = AssistantAudioManager(self)

        # 设置 LangSmith 环境变量
        self._set_langsmith_env()

    def _set_langsmith_env(self):
        """设置 LangSmith 环境变量"""
        if settings.LANGCHAIN_TRACING_V2:
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT
            os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY or ""
            os.environ["LANGCHAIN_ENDPOINT"] = settings.LANGCHAIN_ENDPOINT

    def _create_memory(self):
        """创建符合新规范的内存系统"""
        # 创建消息历史记录
        message_history = ChatMessageHistory()

        # 创建符合新规范的对话内存
        return ConversationBufferWindowMemory(
            chat_memory=message_history,
            k=3,  # 保留最近的3轮对话
            return_messages=True,
            memory_key="chat_history",
            output_key="output"
        )

    def _get_langchain_tools(self):
        """获取LangChain格式的工具集"""
        tools = []
        active_tools = tool_registry.get_all_tools()

        for name, tool_instance in active_tools.items():
            tools.append(LangchainTool(
                name=name,
                func=tool_instance.run,
                description=tool_instance.description
            ))

        return tools

    def _create_agent(self):
        """创建React智能体"""
        # 获取工具名称列表
        tool_names = ", ".join([tool.name for tool in self.tools])

        # 修复：添加tools变量到提示模板
        system_prompt = PromptTemplate(
            template="""
            你是一个智能语音助手，可以帮助用户完成各种任务。
            你可以使用的工具包括：{tools}

            请根据用户的需求选择最合适的工具，并给出友好、有用的回答。
            如果用户的问题不明确，请主动询问更多细节。

            请使用以下格式：
            问题：用户的问题
            思考：你需要思考如何解决问题
            行动：选择要使用的工具（必须是以下工具之一: {tool_names}）
            行动输入：工具的输入
            观察：工具返回的结果
            ...（这个思考/行动/行动输入/观察可以重复多次）
            思考：我现在知道最终答案了
            最终答案：对原始问题的最终回答

            开始！

            问题：{input}
            思考：{agent_scratchpad}
            """,
            input_variables=["input", "agent_scratchpad"],
            partial_variables={
                "tool_names": tool_names,
                "tools": tool_names  # 添加tools变量
            }
        )

        # 创建智能体执行器
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=system_prompt
        )

        return AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=settings.LANGCHAIN_VERBOSE,
            handle_parsing_errors=True,
            callback_manager=langsmith_integration.get_callback_manager()
        )

    def _create_workflow(self):
        """使用StateGraph创建工作流"""
        # 定义状态图
        workflow = StateGraph(AssistantState)

        # 添加节点
        workflow.add_node("speech_recognition", self._speech_recognition_node)
        workflow.add_node("intent_analysis", self._intent_analysis_node)
        workflow.add_node("tool_execution", self._tool_execution_node)
        workflow.add_node("response_generation", self._response_generation_node)
        workflow.add_node("speech_synthesis", self._speech_synthesis_node)

        # 设置入口点
        workflow.set_entry_point("speech_recognition")

        # 添加边
        workflow.add_edge("speech_recognition", "intent_analysis")
        workflow.add_edge("intent_analysis", "tool_execution")
        workflow.add_edge("tool_execution", "response_generation")
        workflow.add_edge("response_generation", "speech_synthesis")
        workflow.add_edge("speech_synthesis", END)

        return workflow.compile()

    # 工作流节点函数
    async def _speech_recognition_node(self, state: AssistantState) -> Dict[str, Any]:
        """语音识别节点"""
        print("开始录音...")
        audio_path = self.speech_utils.record_audio()
        text = self.speech_utils.speech_to_text(audio_path)
        return {
            "audio_path": audio_path,
            "recognized_text": text
        }

    async def _intent_analysis_node(self, state: AssistantState) -> Dict[str, Any]:
        """意图分析节点"""
        text = state.get("recognized_text", "")
        if not text:
            return {"intent": "unknown"}

        # 简单的意图分类
        intents = {
            "weather": any(keyword in text for keyword in ["天气", "气温", "温度", "下雨", "下雪"]),
            "calendar": any(keyword in text for keyword in ["日历", "日程", "会议", "安排", "事件"]),
            "files": any(keyword in text for keyword in ["文件", "查找", "打开", "文件夹", "文档"]),
            "music": any(keyword in text for keyword in ["音乐", "播放", "歌曲", "暂停", "下一首"]),
            "system": any(keyword in text for keyword in ["锁屏", "关机", "打开应用", "系统"]),
            "calculation": any(keyword in text for keyword in ["计算", "算一下", "等于多少", "+", "-", "*", "/"])
        }

        detected_intent = next((intent for intent, detected in intents.items() if detected), "general")
        return {
            "intent": detected_intent,
            "user_input": text
        }

    async def _tool_execution_node(self, state: AssistantState) -> Dict[str, Any]:
        """工具执行节点"""
        user_input = state.get("user_input", "")
        intent = state.get("intent", "general")

        # 根据意图选择工具
        tool_mapping = {
            "weather": "weather_tool",
            "calendar": "calendar_tool",
            "files": "file_tool",
            "music": "music_tool",
            "system": "system_tool",
            "calculation": "calculator_tool"
        }

        tool_name = tool_mapping.get(intent)
        if not tool_name:
            return {"tool_result": self.llm.invoke(user_input)}

        tool = tool_registry.get_tool(tool_name)
        if not tool:
            return {"tool_result": f"抱歉，{tool_name} 工具当前不可用"}

        try:
            result = tool.run(user_input)
            return {"tool_result": result}
        except Exception as e:
            return {"tool_result": f"执行工具时出错: {str(e)}"}

    async def _response_generation_node(self, state: AssistantState) -> Dict[str, Any]:
        """响应生成节点"""
        tool_result = state.get("tool_result", "")
        return {"response_text": tool_result}

    async def _speech_synthesis_node(self, state: AssistantState) -> Dict[str, Any]:
        """语音合成节点"""
        response_text = state.get("response_text", "")
        if response_text:
            self.text_to_speech(response_text)
        return {"synthesis_complete": True}

    def text_to_speech(self, text: str):
        """文本转语音"""
        if text:
            print(f"助手回复: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()

    async def run_voice_mode(self):
        """运行语音模式"""
        print("语音助手已启动（语音模式）")
        print("支持的功能：", ", ".join(tool_registry.get_all_tools().keys()))

        while True:
            try:
                input("按回车开始说话（输入q退出）...")

                # 初始化状态
                initial_state = AssistantState(
                    audio_path=None,
                    recognized_text=None,
                    intent=None,
                    tool_result=None,
                    response_text=None,
                    synthesis_complete=False
                )

                # 使用LangSmith跟踪 - 修复后的方式
                with tracing_v2_enabled(
                        # enabled=settings.LANGCHAIN_TRACING_V2,
                        # tags=["voice-assistant"]
                ):
                    result = await self.workflow.ainvoke(initial_state)

                print("对话完成")

            except KeyboardInterrupt:
                print("\n语音助手已退出")
                break
            except Exception as e:
                print(f"发生错误: {e}")

    async def process_text(self, text: str) -> str:
        """处理文本输入"""
        try:
            # 初始化状态
            initial_state = AssistantState(
                audio_path=None,
                recognized_text=text,
                intent=None,
                tool_result=None,
                response_text=None,
                synthesis_complete=False
            )

            # 使用LangSmith跟踪 - 修复后的方式
            with tracing_v2_enabled(
                    enabled=settings.LANGCHAIN_TRACING_V2,
                    tags=["voice-assistant"]
            ):
                result = await self.workflow.ainvoke(initial_state)

            return result.get("response_text", "抱歉，我无法处理这个请求")
        except Exception as e:
            return f"处理请求时出错: {str(e)}"

    async def start_realtime_mode(self, websocket):
        """启动实时模式"""
        await self.audio_manager.handle_connection(websocket, "")

    def reload_tools(self):
        """重新加载工具配置"""
        tool_registry.reload_config()
        # 重新创建智能体以包含新工具
        self.agent = self._create_agent()
        print("工具配置已重新加载")

    def add_tool(self, name: str, class_path: str, config: Dict[str, Any] = None, enable: bool = True):
        """动态添加新工具"""
        tool_registry.add_dynamic_tool(name, class_path, config, enable)
        # 重新创建智能体以包含新工具
        self.agent = self._create_agent()
        print(f"工具 '{name}' 已添加")

    def remove_tool(self, name: str):
        """移除工具"""
        tool_registry.unregister_tool(name)
        # 重新创建智能体以移除工具
        self.agent = self._create_agent()
        print(f"工具 '{name}' 已移除")

    def log_feedback(self, run_id: str, score: int, comment: str = ""):
        """记录用户反馈到LangSmith"""
        return langsmith_integration.log_feedback(run_id, {
            "score": score,
            "comment": comment
        })

    def analyze_performance(self):
        """分析助手性能"""
        return langsmith_integration.analyze_performance()