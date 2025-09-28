from abc import ABC, abstractmethod

from pydantic import BaseModel, Field


class ToolInput(BaseModel):
    """工具输入模型"""
    query:str = Field(description="用户查询内容")

class BaseAssistantTool(ABC):
    """工具基类"""

    def __init__(self, name: str, config: dict):
        self.name = name

        if config is not None and 'description' in config:
            self.description = config["description"]
        else:
            self.description = ""
        self.config = config
        self.enabled = True

    @abstractmethod
    def run(self, query:str) -> str:
        """运行工具"""
        if not self.enabled:
            return f"{self.name} 工具当前不可用"

        try:
            return self.run(query)
        except Exception as e:
            return f"执行{self.name} 时出错：{str(e)}"


    # def _run(self) -> str:
    #     """工具执行逻辑"""
    #     pass

    def enable(self):
        """启用工具"""
        self.enabled = True

    def disable(self):
        """禁用工具"""
        self.enabled = False