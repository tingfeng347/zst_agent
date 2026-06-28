"""
聊天相关模式
"""
from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., min_length=1, max_length=5000, description="用户消息")
    session_id: Optional[str] = Field(None, description="会话ID")


class ChatMessageSchema(BaseModel):
    """聊天消息"""
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionSchema(BaseModel):
    """聊天会话"""
    id: int
    session_id: str
    title: str
    message_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CreateSessionRequest(BaseModel):
    """创建会话请求"""
    title: Optional[str] = Field(default="新对话", max_length=100)
