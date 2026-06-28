"""
认证 API
"""
from fastapi import APIRouter, HTTPException, status, Request
from app.schemas.auth import UserCreate, UserLogin, TokenResponse, RefreshTokenRequest
from app.schemas.response import ResponseModel
from app.services.auth_service import AuthService

router = APIRouter()

@router.post("/register", response_model=ResponseModel, summary="用户注册")
async def register(user_data: UserCreate):
    """用户注册"""
    try:
        user = await AuthService.register(user_data)
        return ResponseModel(code=200, message="注册成功", data={"user_id": user.id, "username": user.username})
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=ResponseModel[TokenResponse], summary="用户登录")
async def login(form_data: UserLogin, request: Request):
    """用户登录"""
    try:
        user = await AuthService.authenticate(form_data.username, form_data.password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    tokens = await AuthService.create_tokens(user)
    await AuthService.update_login_info(user)
    
    client_host = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    await AuthService.create_login_log(user=user, ip_address=client_host, user_agent=user_agent, status=True, message="登录成功")
    
    return ResponseModel(code=200, message="登录成功", data=tokens)


@router.post("/refresh", response_model=ResponseModel[TokenResponse], summary="刷新令牌")
async def refresh_token(request: RefreshTokenRequest):
    """刷新访问令牌"""
    tokens = await AuthService.refresh_tokens(request.refresh_token)
    
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="刷新令牌无效或已过期",
        )
    
    return ResponseModel(code=200, message="刷新成功", data=tokens)


@router.post("/logout", response_model=ResponseModel, summary="退出登录")
async def logout():
    """退出登录"""
    return ResponseModel(code=200, message="退出成功")
