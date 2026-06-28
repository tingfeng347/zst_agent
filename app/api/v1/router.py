"""
API v1 路由汇总
"""
from fastapi import APIRouter
from app.api.v1 import auth, user, chat, dashboard, knowledge, admin

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(user.router, prefix="/user", tags=["用户"])
api_router.include_router(chat.router, prefix="/chat", tags=["聊天"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["仪表盘"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["知识库"])
api_router.include_router(admin.router, prefix="/admin/users", tags=["管理员"])
