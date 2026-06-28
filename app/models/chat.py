"""
聊天模型
"""
from tortoise import fields
from tortoise.models import Model


class ChatSession(Model):
    """聊天会话模型"""
    
    id = fields.IntField(pk=True)
    session_id = fields.CharField(max_length=50, unique=True, description="会话ID")
    user = fields.ForeignKeyField("models.User", related_name="chat_sessions", on_delete=fields.CASCADE)
    title = fields.CharField(max_length=100, default="新对话", description="会话标题")
    message_count = fields.IntField(default=0, description="消息数量")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "chat_sessions"
        table_description = "聊天会话表"
        ordering = ["-updated_at"]


class ChatMessage(Model):
    """聊天消息模型"""
    
    id = fields.IntField(pk=True)
    session = fields.ForeignKeyField("models.ChatSession", related_name="messages", on_delete=fields.CASCADE)
    role = fields.CharField(max_length=20, description="角色: user/assistant/system")
    content = fields.TextField(description="消息内容")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")

    class Meta:
        table = "chat_messages"
        table_description = "聊天消息表"
        ordering = ["created_at"]
