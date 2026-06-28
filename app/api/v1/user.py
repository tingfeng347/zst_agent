"""
用户 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.user import User
from app.schemas.auth import UserInfo, UserUpdate, PasswordChange
from app.schemas.response import ResponseModel
from app.services.user_service import UserService
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/me", response_model=ResponseModel[UserInfo], summary="获取当前用户信息")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前登录用户的详细信息"""
    return ResponseModel(code=200, message="success", data=UserInfo.model_validate(current_user))


@router.put("/me", response_model=ResponseModel[UserInfo], summary="更新用户信息")
async def update_user_info(update_data: UserUpdate, current_user: User = Depends(get_current_user)):
    """更新当前用户信息"""
    updated_user = await UserService.update_user(current_user, update_data)
    return ResponseModel(code=200, message="更新成功", data=UserInfo.model_validate(updated_user))


@router.post("/change-password", response_model=ResponseModel, summary="修改密码")
async def change_password(password_data: PasswordChange, current_user: User = Depends(get_current_user)):
    """修改密码"""
    try:
        await UserService.change_password(current_user, password_data)
        return ResponseModel(code=200, message="密码修改成功")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/login-logs", response_model=ResponseModel, summary="获取登录日志")
async def get_login_logs(limit: int = 10, current_user: User = Depends(get_current_user)):
    """获取当前用户的登录日志"""
    logs = await UserService.get_login_logs(current_user.id, limit)
    
    logs_data = [
        {
            "id": log.id,
            "ip_address": log.ip_address,
            "user_agent": log.user_agent,
            "browser": log.browser,
            "os": log.os,
            "location": log.location,
            "status": log.status,
            "message": log.message,
            "created_at": log.created_at.isoformat() if log.created_at else None
        }
        for log in logs
    ]
    
    return ResponseModel(code=200, message="success", data=logs_data)
