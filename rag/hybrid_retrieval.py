"""
混合检索服务 - 结合向量检索和标题关键词匹配，支持重排序
"""
import os
import re
import jieba
from typing import List, Dict, Any
from sklearn.metrics.pairwise import cosine_similarity
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rag.vector_store import VectorStoreService
from model.factory import embed_model, reranker
from utils.config_handler import chroma_conf
from utils.logger_handler import logger
from utils.path_tools import get_abs_path
from utils.file_handler import pdf_loader, txt_loader, csv_loader


class HybridRetrievalService:
    """混合检索服务：向量检索 + 标题关键词匹配 + 重排序"""

    def __init__(self, vector_store: VectorStoreService):
        self.vector_store = vector_store
        self.retriever = self.vector_store.get_retriever()
        self.embed_model = embed_model
        self.reranker = reranker
        # 从配置读取参数，提供默认值
        self.rough_match_max = chroma_conf.get("rough_match_max")
        self.fine_match_max = chroma_conf.get("fine_match_max")
        self.final_match_max = chroma_conf.get("final_match_max")
        self.data_path = get_abs_path(chroma_conf.get("data_path", "data"))
        # Embedding API 最大输入长度限制
        self.max_embed_length = 8000
        # 文本分块器，用于将标题匹配到的长文件切块
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_conf.get("chunk_size", 200),
            chunk_overlap=chroma_conf.get("chunk_overlap", 20),
            separators=chroma_conf.get("separators", ["\n\n", "\n", "。", "！", "？", " ", ""]),
            length_function=len,
        )

    def _embed_query(self, text: str) -> List[float]:
        """对查询文本做 Embedding"""
        return self.embed_model.embed_query(text)

    def _embed_documents(self, texts: List[str]) -> List[List[float]]:
        """对多个文本做 Embedding"""
        return self.embed_model.embed_documents(texts)

    def collect_file_metadata(self, folder_path: str) -> List[Dict[str, Any]]:
        """收集知识库文件元数据（路径 + 标题）"""
        file_metadata = []
        if not os.path.exists(folder_path):
            logger.warning(f"[混合检索] 数据目录不存在: {folder_path}")
            return file_metadata

        allowed_types = tuple(chroma_conf.get("allow_knowledge_file_type", ["txt", "pdf", "csv", "md"]))

        for filename in os.listdir(folder_path):
            if not any(filename.endswith(f".{ext}") for ext in allowed_types):
                continue

            # 从文件名提取标题（去掉扩展名）
            title = os.path.splitext(filename)[0].strip()

            # 尝试匹配 "编号-标题.ext" 格式
            title_pattern = re.compile(r'^(.+?)[-_](.*?)$')
            match = title_pattern.match(title)
            if match and match.group(2).strip():
                title = match.group(2).strip()

            file_metadata.append({
                "path": os.path.join(folder_path, filename),
                "title": title
            })

        return file_metadata

    def rough_ranking(self, file_metadata: List[Dict], user_question: str) -> List[Dict]:
        """粗排：基于标题与问题的关键词重合度（Jieba 分词 + 字符重合）"""
        user_question = user_question.strip()
        if not user_question:
            # 问题为空，直接返回空列表（无意义的检索）
            logger.warning("[混合检索] 用户问题为空，跳过粗排")
            return []

        JIEBA_WEIGHT = 0.7

        for item in file_metadata:
            title = item.get("title", "")
            if not title or not title.strip():
                item["rough_score"] = 0
                continue

            # 字符重合度
            question_chars = set(user_question)
            title_chars = set(title.strip())
            char_score = len(question_chars & title_chars) / (len(question_chars) + 1e-6) if question_chars else 0

            # Jieba 分词重合度
            question_words = set(jieba.lcut(user_question))
            title_words = set(jieba.lcut(title.strip()))
            word_score = len(question_words & title_words) / (len(question_words) + 1e-6) if question_words else 0

            combined_score = JIEBA_WEIGHT * word_score + (1 - JIEBA_WEIGHT) * char_score
            item["rough_score"] = combined_score

        sorted_results = sorted(file_metadata, key=lambda x: x.get("rough_score", 0), reverse=True)

        # 过滤掉分词完全不相关的（rough_score为0说明没有任何词重合）
        filtered = [r for r in sorted_results if r.get("rough_score", 0) > 0]
        filtered = filtered[:self.rough_match_max]

        logger.info(f"[混合检索] 粗排：{len(file_metadata)} 个文件，分词过滤后剩 {len(filtered)} 个（最多取 {self.rough_match_max} 个）")
        for r in filtered:
            logger.info(f"  粗排通过: {r['title']} | 分词分: {r['rough_score']:.4f}")

        return filtered

    def fine_ranking(self, rough_results: List[Dict], user_question: str) -> List[Dict]:
        """精排：结合 Embedding 语义相似度和粗排分数"""
        if not rough_results:
            return []

        question_embedding = self._embed_query(user_question)
        titles = [item["title"] for item in rough_results]
        title_embeddings = self._embed_documents(titles)
        semantic_similarities = cosine_similarity([question_embedding], title_embeddings).flatten()

        WEIGHT_ROUGH = 0.5
        WEIGHT_SEMANTIC = 0.5

        for i, item in enumerate(rough_results):
            semantic_score = max(0, float(semantic_similarities[i]))
            rough_score = item.get("rough_score", 0)
            combined_score = WEIGHT_ROUGH * rough_score + WEIGHT_SEMANTIC * semantic_score
            item["semantic_score"] = semantic_score
            item["combined_score"] = combined_score

        sorted_results = sorted(rough_results, key=lambda x: x["combined_score"], reverse=True)
        filtered = sorted_results[:self.fine_match_max]

        logger.info(f"[混合检索] 精排：{len(rough_results)} 个标题，取 Top-{len(filtered)} 个（最多取 {self.fine_match_max} 个）")
        for r in filtered:
            logger.info(f"  精排通过: {r['title']} | 综合分: {r['combined_score']:.4f} | 语义分: {r['semantic_score']:.4f} | 粗排分: {r['rough_score']:.4f}")

        return filtered

    def retrieve(self, user_question: str) -> List[Document]:
        """
        混合检索入口：
        第一路 - 向量库检索 chunk
        第二路 - 标题匹配召回完整文件
        合并去重 + 统一重排序
        """
        all_candidates = []

        # ===== 第一路：向量库直接检索 chunk =====
        try:
            k = chroma_conf.get("k", 3)
            vector_results = self.vector_store.vector_store.similarity_search_with_relevance_scores(user_question, k=k)
            vector_docs = [doc for doc, score in vector_results]
            all_candidates.extend(vector_docs)
            logger.info(f"[混合检索] 向量检索返回 {len(vector_docs)} 条结果：")
            for rank, (doc, score) in enumerate(vector_results, 1):
                source = doc.metadata.get("source", "未知来源")
                preview = doc.page_content[:50].replace("\n", " ")
                logger.info(f"  向量-{rank} | 相似度: {score:.4f} | 来源: {source} | 内容预览: {preview}...")
        except Exception as e:
            logger.error(f"[混合检索] 向量检索失败: {e}")

        # ===== 第二路：标题关键词匹配召回 =====
        try:
            if os.path.exists(self.data_path):
                metadata = self.collect_file_metadata(self.data_path)
                if metadata:
                    rough = self.rough_ranking(metadata, user_question)
                    final_title_matches = self.fine_ranking(rough, user_question)

                    for item in final_title_matches[:5]:
                        try:
                            file_path = item["path"]
                            content = ""
                            
                            # 读取完整文件内容（与参考代码一致）
                            if file_path.endswith(".pdf"):
                                docs = pdf_loader(file_path)
                                content = "\n".join([d.page_content for d in docs])
                            elif file_path.endswith(".csv"):
                                docs = csv_loader(file_path)
                                content = "\n".join([d.page_content for d in docs])
                            elif file_path.endswith((".txt", ".md")):
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()

                            if content:
                                # 先创建完整文档，然后分块（与参考代码思路一致，但最后分块）
                                full_doc = Document(
                                    page_content=content,
                                    metadata={"source": file_path, "title": item["title"]}
                                )
                                # 将完整文档分块
                                chunks = self.splitter.split_documents([full_doc])
                                for chunk in chunks:
                                    chunk.metadata["title"] = item["title"]
                                all_candidates.extend(chunks)
                                logger.info(f"[混合检索] 文件 {item['title']} 分块为 {len(chunks)} 个 chunk")
                        except Exception as e:
                            logger.warning(f"[混合检索] 读取文件失败 {item['path']}: {e}")

                    logger.info(f"[混合检索] 标题匹配召回 {len(final_title_matches)} 个文件")
        except Exception as e:
            logger.error(f"[混合检索] 标题匹配失败: {e}")

        # ===== 去重 =====
        seen = set()
        unique_candidates = []
        for doc in all_candidates:
            key = (doc.metadata.get("source", ""), doc.page_content[:100])
            if key not in seen:
                seen.add(key)
                unique_candidates.append(doc)

        if not unique_candidates:
            logger.warning("[混合检索] 无候选文档")
            return []

        logger.info(f"[混合检索] 去重后共 {len(unique_candidates)} 条候选")

        # ===== 统一重排序（使用 Qwen3-Reranker-8B 模型）=====
        try:
            # 截断超长文本，避免超过 API 输入长度限制
            candidate_texts = [doc.page_content[:self.max_embed_length] for doc in unique_candidates]
            
            # 使用 Reranker 模型进行重排序
            rerank_results = self.reranker.rerank(user_question, candidate_texts)
            
            # rerank_results 格式: [(原始索引, 分数), ...]，已按分数降序排列
            scored_docs = []
            for idx, score in rerank_results:
                if 0 <= idx < len(unique_candidates):
                    scored_docs.append((unique_candidates[idx], score))
                else:
                    logger.warning(f"[混合检索] Reranker 返回的索引 {idx} 超出范围，跳过")
            top_docs = scored_docs[:self.final_match_max]

            logger.info(f"[混合检索] Reranker 重排序后返回 Top-{len(top_docs)} 结果：")
            for rank, (doc, score) in enumerate(top_docs, 1):
                source = doc.metadata.get("source", "未知来源")
                title = doc.metadata.get("title", "")
                preview = doc.page_content[:80].replace("\n", " ")
                logger.info(f"  Top-{rank} | Reranker分数: {score:.4f} | 来源: {source} | 内容预览: {preview}...")

            return [doc for doc, score in top_docs]

        except Exception as e:
            logger.error(f"[混合检索] Reranker 重排序失败: {e}，回退到余弦相似度排序")
            # 回退方案：使用余弦相似度
            try:
                question_emb = self._embed_query(user_question)
                candidate_texts = [doc.page_content[:self.max_embed_length] for doc in unique_candidates]
                candidate_embs = self._embed_documents(candidate_texts)
                similarities = cosine_similarity([question_emb], candidate_embs).flatten()

                scored_docs = [
                    (unique_candidates[i], float(similarities[i]))
                    for i in range(len(unique_candidates))
                ]
                scored_docs.sort(key=lambda x: x[1], reverse=True)
                top_docs = scored_docs[:self.final_match_max]
                return [doc for doc, score in top_docs]
            except Exception as fallback_e:
                logger.error(f"[混合检索] 回退方案也失败: {fallback_e}，返回原始候选")
                return unique_candidates[:self.final_match_max]
