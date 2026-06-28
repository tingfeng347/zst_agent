"""
FastAPI 应用主入口
"""
import os
import sys
import warnings

warnings.filterwarnings(
    "ignore",
    category=SyntaxWarning,
    module=r"jieba(\.|$)",
)

# 添加项目根目录到 Python 路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db, close_db
from app.api.v1.router import api_router

# 初始化知识库（启动时加载向量数据）
def init_knowledge_base():
    """初始化知识库"""
    try:
        from rag.vector_store import VectorStoreService
        vs = VectorStoreService()
        vs.load_document()
        print("✅ 知识库初始化完成")
    except Exception as e:
        print(f"⚠️ 知识库初始化失败: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    print(f"🚀 启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # 初始化数据库
    await init_db()
    print("✅ 数据库连接成功")
    
    # 预热 Agent（在后台异步初始化，不阻塞启动）
    try:
        from app.core.agent_manager import agent_manager
        agent_manager.warmup()  # 在后台线程中预热
        print("✅ Agent 预热已启动（后台初始化中）")
    except Exception as e:
        print(f"⚠️ Agent 预热启动失败: {e}")
    
    # 初始化知识库
    # init_knowledge_base()
    
    yield
    
    # 关闭数据库
    await close_db()
    print("👋 应用已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="智扫通机器人智能客服 API - 集成 RAG 和 Agent",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["根路径"])
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "app": settings.APP_NAME, "version": settings.APP_VERSION}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
