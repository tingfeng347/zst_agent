from langchain_core.tools import tool
from rag.vector_store import VectorStoreService
from rag.rag_service import RagSummarizeService


vector_store = VectorStoreService()
rag = RagSummarizeService(vector_store)


@tool(description="从向量存储中检索参考资料")
def rag_summarize(query: str) -> str:
    return rag.rag_summarize(query, search_mode="hybrid")

@tool(description="无入参，无返回值，调用后触发中间件自动将客服场景切换为聊天场景")
def chat_prompt_switch():
    return "chat_prompt_switch已调用"

@tool(description="无入参，无返回值，调用后触发中间件自动将聊天场景切换为客服场景")
def query_prompt_switch():
    return "query_prompt_switch已调用"




