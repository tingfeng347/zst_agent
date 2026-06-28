"""
用户管理 API（管理员）
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from app.models.user import User
from app.schemas.auth import (
    UserManagementCreate,
    UserManagementUpdate,
    UserManagementResponse,
    UserListResponse
)
from app.schemas.response import ResponseModel
from app.services.user_service import UserService
from app.api.deps import get_current_superuser
from pydantic import BaseModel, Field


class PasswordResetRequest(BaseModel):
    """密码重置请求"""
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")

router = APIRouter()


@router.get("/list", response_model=ResponseModel[UserListResponse], summary="获取用户列表")
async def get_users_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: str = Query(None, description="搜索关键词"),
    sort_by: str = Query("created_at", description="排序字段"),
    sort_order: str = Query("ascending", description="排序方向"),
    current_user: User = Depends(get_current_superuser)
):
    """获取用户列表（仅管理员）"""
    result = await UserService.get_users_list(page=page, page_size=page_size, keyword=keyword, sort_by=sort_by, sort_order=sort_order)
    
    items = [
        UserManagementResponse.model_validate(user)
        for user in result["items"]
    ]
    
    response_data = UserListResponse(
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
        items=items
    )
    
    return ResponseModel(code=200, message="success", data=response_data)


@router.get("/{user_id}", response_model=ResponseModel[UserManagementResponse], summary="获取用户详情")
async def get_user_detail(
    user_id: int,
    current_user: User = Depends(get_current_superuser)
):
    """获取用户详情（仅管理员）"""
    user = await User.filter(id=user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    
    return ResponseModel(code=200, message="success", data=UserManagementResponse.model_validate(user))


@router.post("", response_model=ResponseModel[UserManagementResponse], summary="创建用户")
async def create_user(
    create_data: UserManagementCreate,
    current_user: User = Depends(get_current_superuser)
):
    """创建用户（仅管理员）"""
    try:
        user = await UserService.create_user(create_data)
        return ResponseModel(code=200, message="创建成功", data=UserManagementResponse.model_validate(user))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{user_id}", response_model=ResponseModel[UserManagementResponse], summary="更新用户")
async def update_user(
    user_id: int,
    update_data: UserManagementUpdate,
    current_user: User = Depends(get_current_superuser)
):
    """更新用户信息（仅管理员）"""
    try:
        user = await UserService.update_user_management(user_id, update_data)
        return ResponseModel(code=200, message="更新成功", data=UserManagementResponse.model_validate(user))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{user_id}", response_model=ResponseModel, summary="删除用户")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_superuser)
):
    """删除用户（仅管理员）"""
    if user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不能删除自己")
    
    try:
        await UserService.delete_user(user_id)
        return ResponseModel(code=200, message="删除成功")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{user_id}/reset-password", response_model=ResponseModel, summary="重置密码")
async def reset_user_password(
    user_id: int,
    request: PasswordResetRequest,
    current_user: User = Depends(get_current_superuser)
):
    """重置用户密码（仅管理员）"""
    try:
        await UserService.reset_password(user_id, request.new_password)
        return ResponseModel(code=200, message="密码重置成功")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))