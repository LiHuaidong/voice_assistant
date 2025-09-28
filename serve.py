#!/usr/bin/env python
"""
LangServe 服务入口
"""

from fastapi import FastAPI

from langserve.assistant_chain import AssistantChain
from config import settings
from schemes.models import AssistantRequest, AssistantResponse

# 创建应用
app = FastAPI(
    title="语音助手API",
    version="1.0.0",
    description="提供语音助手功能的API服务"
)

# 创建助手链
assistant_chain = AssistantChain()

add_routes(
    app,
    assistant_chain.chain,
    path="/assistant",
    input_type=AssistantRequest,
    output_type=AssistantResponse,
    enable_feedback_endpoint=True,
    enable_public_trace_link_endpoint=True,
    playground_type="chat"
)

@app.get("/health")
def health_check():
    """健康检查端点"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.LANGSERVE_HOST,
        port=settings.LANGSERVE_PORT
    )