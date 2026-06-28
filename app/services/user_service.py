"""
用户服务
"""
from typing import Optional, List
from datetime import datetime
from tortoise.expressions import Q
from app.models.user import User, LoginLog
from app.schemas.auth import UserUpdate, PasswordChange, UserManagementCreate, UserManagementUpdate
from app.core.security import hash_password, verify_password


class UserService:
    """用户服务类"""
    
    @staticmethod
    async def get_user_by_id(user_id: int) -> Optional[User]:
        """根据 ID 获取用户"""
        return await User.filter(id=user_id, is_active=True).first()
    
    @staticmethod
    async def update_user(user: User, update_data: UserUpdate) -> User:
        """更新用户信息"""
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(user, field, value)
        await user.save()
        return user
    
    @staticmethod
    async def change_password(user: User, password_data: PasswordChange) -> bool:
        """修改密码"""
        if not verify_password(password_data.old_password, user.hashed_password):
            raise ValueError("旧密码错误")
        
        user.hashed_password = hash_password(password_data.new_password)
        await user.save()
        return True
    
    @staticmethod
    async def get_login_logs(user_id: int, limit: int = 10) -> List[LoginLog]:
        """获取用户登录日志"""
        return await LoginLog.filter(user_id=user_id).order_by("-created_at").limit(limit)
    
    @staticmethod
    async def get_statistics():
        """获取用户统计数据"""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        total_users = await User.all().count()
        
        today_logins = await LoginLog.filter(created_at__gte=today, status=True).values_list("user_id", flat=True)
        today_login_count = len(set(today_logins))
        
        today_operations = await LoginLog.filter(created_at__gte=today).count()
        active_users = await User.filter(is_active=True).count()
        
        return {
            "total_users": total_users,
            "today_login_count": today_login_count,
            "today_operations": today_operations,
            "active_users": active_users
        }
    
    @staticmethod
    async def get_users_list(page: int = 1, page_size: int = 10, keyword: Optional[str] = None, sort_by: str = "created_at", sort_order: str = "ascending"):
        """获取用户列表（分页）"""
        query = User.all()
        
        if keyword:
            query = query.filter(
                Q(username__icontains=keyword) | Q(email__icontains=keyword) | Q(nickname__icontains=keyword)
            )
        
        total = await query.count()
        offset = (page - 1) * page_size
        
        sort_field = sort_by
        if sort_order == "descending":
            sort_field = f"-{sort_by}"
        
        users = await query.order_by(sort_field).offset(offset).limit(page_size)
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": users
        }
    
    @staticmethod
    async def create_user(create_data: UserManagementCreate) -> User:
        """创建用户"""
        existing_user = await User.filter(
            username=create_data.username
        ).or_(
            email=create_data.email
        ).first()
        
        if existing_user:
            if existing_user.username == create_data.username:
                raise ValueError("用户名已存在")
            else:
                raise ValueError("邮箱已存在")
        
        user = await User.create(
            username=create_data.username,
            email=create_data.email,
            hashed_password=hash_password(create_data.password),
            nickname=create_data.nickname,
            phone=create_data.phone,
            is_superuser=create_data.is_superuser,
            is_active=True
        )
        return user
    
    @staticmethod
    async def update_user_management(user_id: int, update_data: UserManagementUpdate) -> User:
        """管理员更新用户"""
        user = await User.filter(id=user_id).first()
        if not user:
            raise ValueError("用户不存在")
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(user, field, value)
        await user.save()
        return user
    
    @staticmethod
    async def delete_user(user_id: int) -> bool:
        """删除用户"""
        user = await User.filter(id=user_id).first()
        if not user:
            raise ValueError("用户不存在")
        
        await user.delete()
        return True
    
    @staticmethod
    async def reset_password(user_id: int, new_password: str) -> bool:
        """重置用户密码"""
        user = await User.filter(id=user_id).first()
        if not user:
            raise ValueError("用户不存在")
        
        user.hashed_password = hash_password(new_password)
        await user.save()
        return True
