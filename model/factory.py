from abc import ABC
from abc import abstractmethod
import requests
from langchain_community.chat_models.tongyi import ChatTongyi, BaseChatModel
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.embeddings import Embeddings
from typing import Optional, List, Tuple

from app.core.config import settings
from utils.logger_handler import logger


class BaseModelFactory(ABC):
    @abstractmethod
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        pass

class ChatModelFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return ChatTongyi(model=settings.CHAT_MODEL_NAME)


class EmbeddingsFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return DashScopeEmbeddings(model=settings.EMBEDDING_MODEL_NAME)


class RerankerService:
    """Reranker 服务"""
    
    def __init__(self):
        self.api_url = settings.RERANKER_API_URL
        self.model = settings.RERANKER_MODEL
        self.token = settings.RERANKER_API_KEY
        
        if not self.token:
            logger.warning(f"[Reranker] 未设置 RERANKER_API_KEY 环境变量，重排序功能可能无法使用")
    
    def rerank(self, query: str, documents: List[str]) -> List[Tuple[int, float]]:
        """
        对文档进行重排序
        
        Args:
            query: 查询文本
            documents: 文档列表
            
        Returns:
            List[Tuple[int, float]]: [(原始索引, 分数), ...]，按分数降序排列
        """
        if not self.token:
            logger.error("[Reranker] API token 未配置，无法进行重排序")
            return [(i, 0.0) for i in range(len(documents))]
        
        if not documents:
            return []
        
        try:
            payload = {
                "model": self.model,
                "query": query,
                "documents": documents
            }
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            print(response.text)
            response.raise_for_status()
            
            result = response.json()
            
            # 解析返回结果，格式通常是: [{"index": 0, "relevance_score": 0.95}, ...]
            if isinstance(result, dict) and "results" in result:
                results = result["results"]
            elif isinstance(result, list):
                results = result
            else:
                logger.error(f"[Reranker] 返回格式异常: {result}")
                return [(i, 0.0) for i in range(len(documents))]
            
            # 转换为 (索引, 分数) 元组列表
            scored_results = []
            for item in results:
                if isinstance(item, dict):
                    idx = item.get("index", item.get("idx", 0))
                    score = item.get("relevance_score", item.get("score", 0.0))
                    scored_results.append((idx, float(score)))
                else:
                    logger.warning(f"[Reranker] 结果项格式异常: {item}")
            
            # 按分数降序排序
            scored_results.sort(key=lambda x: x[1], reverse=True)
            
            logger.info(f"[Reranker] 成功对 {len(documents)} 个文档进行重排序")
            return scored_results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"[Reranker] API 请求失败: {e}")
            return [(i, 0.0) for i in range(len(documents))]
        except Exception as e:
            logger.error(f"[Reranker] 重排序失败: {e}")
            return [(i, 0.0) for i in range(len(documents))]


class RerankerFactory:
    """Reranker 工厂类"""
    _instance: Optional[RerankerService] = None
    
    @classmethod
    def generator(cls) -> RerankerService:
        if cls._instance is None:
            cls._instance = RerankerService()
        return cls._instance


chat_model = ChatModelFactory().generator()
embed_model = EmbeddingsFactory().generator()
reranker = RerankerFactory.generator()