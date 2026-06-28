"""
用户模型
"""
from tortoise import fields
from tortoise.models import Model


class User(Model):
    """用户模型"""
    
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True, description="用户名")
    email = fields.CharField(max_length=100, unique=True, description="邮箱")
    hashed_password = fields.CharField(max_length=255, description="密码哈希")
    nickname = fields.CharField(max_length=50, null=True, description="昵称")
    avatar = fields.CharField(max_length=255, null=True, description="头像URL")
    phone = fields.CharField(max_length=20, null=True, description="手机号")
    is_active = fields.BooleanField(default=True, description="是否激活")
    is_superuser = fields.BooleanField(default=False, description="是否超级管理员")
    login_count = fields.IntField(default=0, description="登录次数")
    last_login = fields.DatetimeField(null=True, description="最后登录时间")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        table = "users"
        table_description = "用户表"
        ordering = ["-created_at"]


class LoginLog(Model):
    """登录日志模型"""
    
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="login_logs", on_delete=fields.CASCADE)
    ip_address = fields.CharField(max_length=45, null=True, description="IP地址")
    user_agent = fields.CharField(max_length=500, null=True, description="用户代理")
    browser = fields.CharField(max_length=100, null=True, description="浏览器")
    os = fields.CharField(max_length=100, null=True, description="操作系统")
    location = fields.CharField(max_length=200, null=True, description="登录地点")
    status = fields.BooleanField(default=True, description="登录状态")
    message = fields.CharField(max_length=200, null=True, description="登录消息")
    created_at = fields.DatetimeField(auto_now_add=True, description="登录时间")

    class Meta:
        table = "login_logs"
        table_description = "登录日志表"
        ordering = ["-created_at"]
