"""
认证服务
"""
from datetime import datetime
from typing import Optional
from app.models.user import User, LoginLog
from app.schemas.auth import UserCreate, TokenResponse
from app.core.security import (
    hash_password, 
    verify_password, 
    create_access_token, 
    create_refresh_token,
    verify_refresh_token
)
from app.core.config import settings


class AuthService:
    """认证服务类"""
    
    @staticmethod
    async def register(user_data: UserCreate) -> User:
        """用户注册"""
        # 检查用户名是否已存在
        existing_user = await User.filter(username=user_data.username).first()
        if existing_user:
            raise ValueError("用户名已存在")
        
        # 检查邮箱是否已存在
        existing_email = await User.filter(email=user_data.email).first()
        if existing_email:
            raise ValueError("邮箱已被注册")
        
        # 创建用户
        user = await User.create(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            nickname=user_data.nickname or user_data.username
        )
        return user
    
    @staticmethod
    async def authenticate(username: str, password: str) -> Optional[User]:
        """用户认证"""
        # 支持用户名或邮箱登录
        user = await User.filter(username=username).first()
        if not user:
            user = await User.filter(email=username).first()
        
        if not user:
            raise ValueError("无此用户")
        
        if not user.is_active:
            raise ValueError("账号已被禁用")
        
        if not verify_password(password, user.hashed_password):
            raise ValueError("密码错误")
        
        return user
    
    @staticmethod
    async def create_tokens(user: User) -> TokenResponse:
        """创建认证令牌"""
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    @staticmethod
    async def refresh_tokens(refresh_token: str) -> Optional[TokenResponse]:
        """刷新令牌"""
        payload = verify_refresh_token(refresh_token)
        if not payload:
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        user = await User.filter(id=int(user_id), is_active=True).first()
        if not user:
            return None
        
        return await AuthService.create_tokens(user)
    
    @staticmethod
    async def update_login_info(user: User):
        """更新用户登录信息"""
        user.login_count += 1
        user.last_login = datetime.now()
        await user.save()
    
    @staticmethod
    async def create_login_log(user: User, ip_address: str = None, user_agent: str = None, 
                               status: bool = True, message: str = None):
        """创建登录日志"""
        await LoginLog.create(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            message=message
        )
