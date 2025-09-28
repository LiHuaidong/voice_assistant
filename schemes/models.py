from pydantic import BaseModel

class AssistantRequest(BaseModel):
    """API 请求模型"""
    input: str
    context: dict = {}
    user_id: str = None

class AssistantResponse(BaseModel):
    """API 响应模型"""
    output: str
    context: dict = {}