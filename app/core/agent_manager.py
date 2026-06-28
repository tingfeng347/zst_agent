"""
Agent 管理器 - 全局单例，用于预热和复用 Agent
"""
import asyncio
import threading
from typing import Optional
from utils.logger_handler import logger


class AgentManager:
    """Agent 管理器 - 单例模式"""
    _instance = None
    _lock = threading.Lock()
    _agent = None
    _initialized = False
    _initializing = False
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(AgentManager, cls).__new__(cls)
        return cls._instance
    
    def get_agent(self):
        """获取 Agent 实例（如果已初始化）"""
        if self._agent is not None:
            return self._agent
        return None
    
    def is_ready(self) -> bool:
        """检查 Agent 是否已准备好"""
        return self._initialized and self._agent is not None
    
    def is_initializing(self) -> bool:
        """检查 Agent 是否正在初始化"""
        return self._initializing
    
    def _init_agent(self):
        """初始化 Agent（同步方法，在后台线程中运行）"""
        if self._agent is not None:
            return
        
        if self._initializing:
            return
        
        try:
            self._initializing = True
            logger.info("[AgentManager] 开始初始化 Agent...")
            
            from agent.react_agent import ReactAgent
            self._agent = ReactAgent()
            self._initialized = True
            
            logger.info("[AgentManager] Agent 初始化完成")
        except Exception as e:
            logger.error(f"[AgentManager] Agent 初始化失败: {e}")
            self._initialized = False
            self._agent = None
        finally:
            self._initializing = False
    
    def warmup(self):
        """预热 Agent（在后台线程中异步初始化）"""
        if self._agent is not None or self._initializing:
            return
        
        def init_in_thread():
            """在后台线程中初始化"""
            self._init_agent()
        
        thread = threading.Thread(target=init_in_thread, daemon=True)
        thread.start()
        logger.info("[AgentManager] 已启动 Agent 预热线程")
    
    async def warmup_async(self):
        """异步预热 Agent"""
        if self._agent is not None or self._initializing:
            return
        
        def init_agent():
            self._init_agent()
        
        # 在线程池中执行初始化，不阻塞事件循环
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, init_agent)


# 全局单例实例
agent_manager = AgentManager()
