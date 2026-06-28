"""
应用配置模块 - 使用 Pydantic Settings 管理配置
"""
from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基础配置
    APP_NAME: str = "智扫通机器人智能客服"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 项目根目录
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # API 配置
    API_V1_PREFIX: str = "/api/v1"
    
    # JWT 配置
    SECRET_KEY: str = "zst-agent-secret-key-change-in-production-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # MySQL 数据库配置
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "123456"
    MYSQL_DATABASE: str = "zst_agent"
    
    # CORS 配置
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173", 
        "http://localhost:3000", 
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ]
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    
    # 模型配置
    CHAT_MODEL_NAME: str = "qwen3-max"
    EMBEDDING_MODEL_NAME: str = "text-embedding-v4"
    
    # DashScope API
    DASHSCOPE_API_KEY: str = ""
    
    # Reranker 重排序
    RERANKER_API_URL: str = "https://api.siliconflow.cn/v1/rerank"
    RERANKER_MODEL: str = "BAAI/bge-reranker-v2-m3"
    RERANKER_API_KEY: str = ""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取缓存的配置实例"""
    return Settings()


settings = get_settings()
