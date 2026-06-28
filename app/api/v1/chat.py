"""
聊天 API - 支持流式输出和思考过程
"""
import json
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatSessionSchema, ChatMessageSchema, CreateSessionRequest
from app.schemas.response import ResponseModel
from app.services.chat_service import ChatService
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/stream", summary="流式聊天")
async def chat_stream(request: ChatRequest, current_user: User = Depends(get_current_user)):
    """
    流式聊天接口（SSE）
    
    返回的数据类型：
    - thinking: 思考过程（可折叠）
    - content: 回答内容（逐字输出）
    - done: 完成标记
    - session_id: 会话ID
    """
    chat_service = ChatService(user_id=current_user.id)
    
    async def event_generator():
        async for chunk in chat_service.chat_stream(request.message, request.session_id):
            yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.get("/sessions", response_model=ResponseModel, summary="获取会话列表")
async def get_sessions(limit: int = 20, current_user: User = Depends(get_current_user)):
    """获取当前用户的会话列表"""
    chat_service = ChatService(user_id=current_user.id)
    sessions = await chat_service.get_sessions(limit)
    sessions_data = [ChatSessionSchema.model_validate(s).model_dump() for s in sessions]
    return ResponseModel(code=200, message="success", data=sessions_data)


@router.post("/sessions", response_model=ResponseModel, summary="创建新会话")
async def create_session(request: CreateSessionRequest, current_user: User = Depends(get_current_user)):
    """创建新的聊天会话"""
    chat_service = ChatService(user_id=current_user.id)
    session = await chat_service.create_session(request.title)
    return ResponseModel(code=200, message="创建成功", data=ChatSessionSchema.model_validate(session).model_dump())


@router.get("/sessions/{session_id}", response_model=ResponseModel, summary="获取会话详情")
async def get_session(session_id: str, current_user: User = Depends(get_current_user)):
    """获取指定会话的详情和消息历史"""
    chat_service = ChatService(user_id=current_user.id)
    session = await chat_service.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")
    
    messages = await chat_service.get_history(session_id)
    
    return ResponseModel(
        code=200,
        message="success",
        data={
            "session": ChatSessionSchema.model_validate(session).model_dump(),
            "messages": [ChatMessageSchema.model_validate(msg).model_dump() for msg in messages]
        }
    )


@router.delete("/sessions/{session_id}", response_model=ResponseModel, summary="删除会话")
async def delete_session(session_id: str, current_user: User = Depends(get_current_user)):
    """删除指定会话"""
    chat_service = ChatService(user_id=current_user.id)
    success = await chat_service.delete_session(session_id)
    
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")
    
    return ResponseModel(code=200, message="删除成功")


@router.get("/statistics", response_model=ResponseModel, summary="获取聊天统计")
async def get_chat_statistics(current_user: User = Depends(get_current_user)):
    """获取当前用户的聊天统计数据"""
    stats = await ChatService.get_chat_statistics(current_user.id)
    return ResponseModel(code=200, message="success", data=stats)
