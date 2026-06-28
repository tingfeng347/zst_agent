from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from rag.vector_store import VectorStoreService
from rag.hybrid_retrieval import HybridRetrievalService
from utils.logger_handler import logger
from utils.config_handler import prompts_conf
from model.factory import chat_model
from utils.path_tools import get_abs_path

# def print_prompt(prompt):
#     print("="*20)
#     print(prompt.to_string())
#     print("="*20)
#     return prompt

class RagSummarizeService:
    # 类变量缓存，所有实例共用
    _PROMPT_TEXT: str = None

    def __init__(self, vector_store: VectorStoreService):
        self.vector_store = vector_store
        self.retriever = self.vector_store.get_retriever()
        self.hybrid_service = HybridRetrievalService(vector_store)
        self.prompt_text = self._load_prompt_text()
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)
        self.model = chat_model
        self.chain = self._init_chain()

    def _load_prompt_text(self) -> str:
        if self._PROMPT_TEXT is not None:
            # 避免重复创建对象的重复读文件加载，从缓存读取
            return self._PROMPT_TEXT

        path = get_abs_path(prompts_conf["rag_summarize_prompt_path"])
        try:
            with open(path, "r", encoding="utf-8") as f:
                prompt_text = f.read().strip()
        except PermissionError:
            logger.error(f"无权限读取提示词文件：{path}")
            raise PermissionError(f"无权限读取提示词文件：{path}")
        except UnicodeDecodeError:
            logger.error(f"提示词文件编码错误（需UTF-8）：{path}")
            raise ValueError(f"提示词文件编码错误（需UTF-8）：{path}")
        except Exception as e:
            logger.error(f"读取提示词文件失败：{str(e)}")
            raise RuntimeError(f"读取提示词文件失败：{str(e)}")

        if not prompt_text:
            logger.error(f"提示词文件内容为空：{path}")
            raise ValueError(f"提示词文件内容为空：{path}")

        # 记录缓存
        self._PROMPT_TEXT = prompt_text
        return prompt_text

    def _init_chain(self):
        chain = self.prompt_template | self.model | StrOutputParser()
        return chain

    def retrieve_docs(self, query: str) -> list[Document]:
        """向量检索（默认模式）"""
        return self.retriever.invoke(query)

    def retrieve_docs_hybrid(self, query: str) -> list[Document]:
        """混合检索模式"""
        return self.hybrid_service.retrieve(query)

    def rag_summarize(self, query: str, search_mode: str) -> str:
        """
        RAG 总结
        :param query: 用户问题
        :param search_mode: 检索模式 - "vector"(向量检索) 或 "hybrid"(混合检索)
        """
        input_dict = {}

        if search_mode == "hybrid":
            context_docs = self.retrieve_docs_hybrid(query)
        else:
            context_docs = self.retrieve_docs(query)

        context = ""
        counter = 0
        for doc in context_docs:
            counter += 1
            context += f"【参考资料{counter}】：参考资料：{doc.page_content} | 参考元数据：{doc.metadata}\n"
        print(context)
        input_dict["input"] = query
        input_dict["context"] = context

        return self.chain.invoke(input_dict)


# for testing
# if __name__ == '__main__':
#     vs = VectorStoreService()
#     rag = RagSummarizeService(vs)
#     print(rag.rag_summarize("小户型适合哪种扫地机器人？"))
