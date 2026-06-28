"""
数据库配置模块 - Tortoise ORM 配置
"""
from tortoise import Tortoise
from app.core.config import settings

# Tortoise ORM 配置
TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "host": settings.MYSQL_HOST,
                "port": settings.MYSQL_PORT,
                "user": settings.MYSQL_USER,
                "password": settings.MYSQL_PASSWORD,
                "database": settings.MYSQL_DATABASE,
                "charset": "utf8mb4",
                "minsize": 1,
                "maxsize": 10,
            }
        }
    },
    "apps": {
        "models": {
            "models": ["app.models"],
            "default_connection": "default",
        }
    },
    "use_tz": False,
    "timezone": "Asia/Shanghai",
}


async def init_db():
    """初始化数据库连接"""
    await Tortoise.init(config=TORTOISE_ORM)
    # await Tortoise.generate_schemas(safe=True)


async def close_db():
    """关闭数据库连接"""
    await Tortoise.close_connections()
