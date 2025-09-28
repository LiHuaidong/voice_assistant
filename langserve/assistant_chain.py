from langchain_core.runnables import RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models import ChatOllama

from core.assistant import VoiceAssistant
from config import settings


class AssistantChain:
    """LangServe 链定义"""

    def __init__(self):
        self.assistant = VoiceAssistant()

        # 创建 LangChain 链
        self.chain = self._create_chain()

    def _create_chain(self):
        """创建 LangChain 链"""
        # 系统提示
        system_prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个智能语音助手，可以帮助用户完成各种任务。"),
            ("user", "{input}")
        ])

        # 创建链
        chain = (
                system_prompt
                | ChatOllama(model=settings.LLM_MODEL, temperature=0.7)
                | StrOutputParser()
        )

        # 包装处理函数
        return RunnableLambda(self._process_input) | chain

    def _process_input(self, input_data: dict) -> dict:
        """处理输入数据"""
        user_input = input_data.get("input", "")
        context = input_data.get("context", {})

        # 使用助手处理输入
        response = self.assistant.process_text(user_input)

        return {"input": response}

    def invoke(self, input_data: dict) -> dict:
        """调用链"""
        return self.chain.invoke(input_data)