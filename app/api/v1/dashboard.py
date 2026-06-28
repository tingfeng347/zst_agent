"""
仪表盘 API
"""
from datetime import datetime
from fastapi import APIRouter, Depends
from app.models.user import User
from app.schemas.response import ResponseModel
from app.services.user_service import UserService
from app.services.chat_service import ChatService
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/statistics", response_model=ResponseModel, summary="获取仪表盘统计数据")
async def get_dashboard_statistics(current_user: User = Depends(get_current_user)):
    """获取仪表盘统计数据"""
    user_stats = await UserService.get_statistics()
    chat_stats = await ChatService.get_chat_statistics(current_user.id)
    
    return ResponseModel(
        code=200,
        message="success",
        data={
            "unread_notifications": 9,
            "total_notifications": 279,
            "today_login_count": user_stats["today_login_count"],
            "today_operations": user_stats["today_operations"],
            "total_sessions": chat_stats["total_sessions"],
            "total_messages": chat_stats["total_messages"]
        }
    )


@router.get("/user-info", response_model=ResponseModel, summary="获取仪表盘用户信息")
async def get_dashboard_user_info(current_user: User = Depends(get_current_user)):
    """获取仪表盘显示的用户信息"""
    now = datetime.now()
    hour = now.hour
    
    if 5 <= hour < 12:
        greeting = "上午好"
    elif 12 <= hour < 14:
        greeting = "中午好"
    elif 14 <= hour < 18:
        greeting = "下午好"
    else:
        greeting = "晚上好"
    
    role_name = "超级管理员" if current_user.is_superuser else "普通用户"
    
    weekdays = {0: "星期一", 1: "星期二", 2: "星期三", 3: "星期四", 4: "星期五", 5: "星期六", 6: "星期日"}
    
    return ResponseModel(
        code=200,
        message="success",
        data={
            "greeting": greeting,
            "username": current_user.nickname or current_user.username,
            "role": role_name,
            "department": "智能客服中心",
            "current_time": now.strftime("%H:%M:%S"),
            "current_date": f"{now.strftime('%Y年%m月%d日')} {weekdays[now.weekday()]}"
        }
    )


@router.get("/recent-activities", response_model=ResponseModel, summary="获取最近活动")
async def get_recent_activities(limit: int = 10, current_user: User = Depends(get_current_user)):
    """获取最近的活动记录"""
    from app.models.chat import ChatMessage
    
    messages = await ChatMessage.filter(session__user_id=current_user.id).order_by("-created_at").limit(limit).prefetch_related("session")
    
    activities = []
    for msg in messages:
        activities.append({
            "type": "chat",
            "title": f"{'发送消息' if msg.role == 'user' else '收到回复'}",
            "content": msg.content[:50] + ("..." if len(msg.content) > 50 else ""),
            "session_title": msg.session.title if msg.session else "未知会话",
            "created_at": msg.created_at.isoformat() if msg.created_at else None
        })
    
    return ResponseModel(code=200, message="success", data=activities)
