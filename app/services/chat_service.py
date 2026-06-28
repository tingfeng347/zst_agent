"""
聊天服务 - 集成原有的 RAG 和 Agent，支持流式输出
"""
import uuid
import asyncio
import re
from typing import Optional, List, AsyncGenerator
from app.models.chat import ChatSession, ChatMessage
from app.schemas.chat import ChatSessionSchema, ChatMessageSchema


class ChatService:
    """聊天服务类"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self._agent = None
        self._rag_service = None
        self._use_rag_fallback = False
    
    def _get_agent(self):
        """获取 Agent 实例（优先使用全局单例）"""
        # 优先使用全局 Agent 管理器中的实例
        from app.core.agent_manager import agent_manager
        global_agent = agent_manager.get_agent()
        
        if global_agent is not None:
            return global_agent
        
        # 如果全局 Agent 还未初始化，尝试使用本地实例
        if self._agent is not None:
            return self._agent
        
        if self._use_rag_fallback:
            return None
        
        # 如果全局 Agent 正在初始化，等待一下
        if agent_manager.is_initializing():
            # 等待一小段时间，让初始化完成（最多等待 3 秒）
            import time
            for _ in range(30):  # 每次等待 0.1 秒，最多等待 3 秒
                time.sleep(0.1)
                global_agent = agent_manager.get_agent()
                if global_agent is not None:
                    return global_agent
        
        # 如果全局 Agent 初始化失败，尝试本地初始化（降级方案）
        try:
            from agent.react_agent import ReactAgent
            self._agent = ReactAgent()
            return self._agent
        except Exception as e:
            print(f"⚠️ 加载 Agent 失败: {e}")
            self._use_rag_fallback = True
            return None
    
    def _get_rag_service(self):
        """获取 RAG 服务作为备用"""
        if self._rag_service is None:
            try:
                from rag.vector_store import VectorStoreService
                from rag.rag_service import RagSummarizeService
                vs = VectorStoreService()
                self._rag_service = RagSummarizeService(vs)
            except Exception as e:
                print(f"⚠️ 加载 RAG 服务失败: {e}")
        return self._rag_service

    
    async def create_session(self, title: str = "新对话") -> ChatSession:
        """创建新会话"""
        session_id = str(uuid.uuid4())[:8]
        session = await ChatSession.create(
            session_id=session_id,
            user_id=self.user_id,
            title=title
        )
        return session
    
    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        """获取会话"""
        return await ChatSession.filter(session_id=session_id, user_id=self.user_id).first()
    
    async def get_or_create_session(self, session_id: Optional[str] = None) -> ChatSession:
        """获取或创建会话"""
        if session_id:
            session = await self.get_session(session_id)
            if session:
                return session
        return await self.create_session()
    
    async def get_sessions(self, limit: int = 20) -> List[ChatSession]:
        """获取用户的所有会话"""
        return await ChatSession.filter(user_id=self.user_id).order_by("-updated_at").limit(limit)
    
    async def delete_session(self, session_id: str) -> bool:
        """删除会话（硬删除，从数据库中彻底删除）"""
        session = await self.get_session(session_id)
        if session:
            # 先删除关联的消息
            await ChatMessage.filter(session=session).delete()
            # 再删除会话本身
            await session.delete()
            return True
        return False
    
    async def add_message(self, session: ChatSession, role: str, content: str, tokens: int = 0) -> ChatMessage:
        """添加消息"""
        message = await ChatMessage.create(
            session=session,
            role=role,
            content=content,
            tokens=tokens
        )
        
        session.message_count += 1
        if session.message_count == 1 and role == "user":
            session.title = content[:20] + ("..." if len(content) > 20 else "")
        await session.save()
        
        return message
    
    async def get_history(self, session_id: str) -> List[ChatMessage]:
        """获取会话历史"""
        session = await self.get_session(session_id)
        if not session:
            return []
        return await ChatMessage.filter(session=session).order_by("created_at")
    
    async def chat_stream(self, message: str, session_id: Optional[str] = None) -> AsyncGenerator[dict, None]:
        """
        流式聊天 - 只输出最终答案，不输出思考过程
        
        Args:
            message: 用户消息
            session_id: 会话ID
        
        Yields:
            dict: {
                "type": "content" | "done" | "session_id",
                "data": ...
            }
        """
        session = await self.get_or_create_session(session_id)
        
        # 先发送 session_id，确保前端能绑定到正确的会话
        yield {"type": "session_id", "data": session.session_id}
        
        await self.add_message(session, "user", message)
        
        final_answer = ""
        
        try:
            agent = self._get_agent()
            
            # 获取历史消息作为上下文
            history = await self.get_history(session.session_id)
            context = "\n".join([f"{msg.role}: {msg.content}" for msg in history])
            full_message = f"Context:\n{context}\n\nCurrent message:{message}"
            
            if agent is not None:
                # 使用原有 Agent（异步流式处理）
                chunks = []
                async for chunk in agent.execute_stream(full_message):
                    chunks.append(chunk)
                
                # 获取最后一个完整响应
                if chunks:
                    # 提取最终答案，去除思考过程
                    final_answer = chunks[-1]
                    
                # 逐字发送最终答案实现打字机效果
                for char in final_answer:
                    yield {
                        "type": "content",
                        "data": char
                    }
                    await asyncio.sleep(0.01)  # 控制打字速度
            else:
                # Agent 不可用，返回错误消息
                final_answer = "你好！我是智扫通智能客服。\n\n抱歉，智能服务暂时不可用，请稍后再试。"
                for char in final_answer:
                    yield {
                        "type": "content",
                        "data": char
                    }
                    await asyncio.sleep(0.02)
            
        except Exception as e:
            error_msg = f"抱歉，处理您的请求时出现错误：{str(e)}"
            final_answer = error_msg
            for char in error_msg:
                yield {
                    "type": "content",
                    "data": char
                }
                await asyncio.sleep(0.02)
        
        # 保存完整响应
        await self.add_message(session, "assistant", final_answer)
        
        # 发送完成标记
        yield {"type": "done", "data": None}
    
    @staticmethod
    async def get_chat_statistics(user_id: int):
        """获取聊天统计"""
        total_sessions = await ChatSession.filter(user_id=user_id).count()
        total_messages = await ChatMessage.filter(session__user_id=user_id).count()
        
        return {
            "total_sessions": total_sessions,
            "total_messages": total_messages
        }
