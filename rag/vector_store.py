from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from model.factory import embed_model
from langchain_chroma import Chroma
from utils.config_handler import chroma_conf
import os
from utils.file_handler import get_file_md5_hex, listdir_with_allowed_type, csv_loader, pdf_loader, txt_loader
from utils.logger_handler import logger
from utils.path_tools import get_abs_path

# 定义向量存储服务类，用于处理文档的加载、分片、向量存储及检索
class VectorStoreService:
    # 类构造函数，初始化向量存储和文本分割器
    def __init__(self):
        # 初始化Chroma向量存储实例，配置集合名称、嵌入模型、持久化目录
        self.vector_store = Chroma(
            collection_name=chroma_conf["collection_name"],  # 从配置中获取集合名称
            embedding_function=embed_model,  # 使用预定义的嵌入模型
            persist_directory=get_abs_path(chroma_conf["persist_directory"]),  # 获取持久化目录的绝对路径
        )

        # 初始化递归文本分割器，用于将大文档分割为小片段
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_conf["chunk_size"],  # 从配置中获取每个分片的大小
            chunk_overlap=chroma_conf["chunk_overlap"],  # 分片之间的重叠长度
            separators=chroma_conf["separators"],  # 分片的分隔符
            length_function=len,  # 计算文本长度的函数，这里使用内置的len
        )

    # 获取向量存储的检索器实例，用于后续的相似性检索
    def get_retriever(self):
        # 返回检索器，设置搜索参数k为配置中的值（返回top k个相似结果）
        return self.vector_store.as_retriever(search_kwargs={"k": chroma_conf["k"]})

    # 加载指定目录下的文档到向量存储中
    def load_document(self):
        # 嵌套函数：检查文件的MD5值是否已存在于存储的MD5文件中，避免重复加载
        def check_md5_hex(md5_for_check):
            # 如果MD5存储文件不存在，创建空文件并返回False
            if not os.path.exists(get_abs_path(chroma_conf["md5_hex_store"])):
                open(get_abs_path(chroma_conf["md5_hex_store"]), "w", encoding="utf-8").close()
                return False

            # 读取MD5存储文件，逐行检查目标MD5是否存在
            with open(get_abs_path(chroma_conf["md5_hex_store"]), "r", encoding="utf-8") as f:
                for line in f.readlines():
                    line = line.strip()  # 去除行首尾的空白字符
                    if line == md5_for_check:
                        return True  # 找到匹配的MD5，返回True

            return False  # 未找到匹配的MD5，返回False

        # 嵌套函数：将文件的MD5值保存到MD5存储文件中
        def save_md5_hex(md5_for_save):
            # 以追加模式打开MD5存储文件，写入MD5值并换行
            with open(get_abs_path(chroma_conf["md5_hex_store"]), "a", encoding="utf-8") as f:
                f.write(md5_for_save+"\n")

        # 嵌套函数：根据文件类型调用对应的加载器，加载文档内容为Document对象列表
        def get_file_documents(read_path: str):
            if read_path.endswith("txt"):  # 处理txt文件
                return txt_loader(read_path)
            elif read_path.endswith("pdf"):  # 处理pdf文件
                return pdf_loader(read_path)
            elif read_path.endswith("csv"):  # 处理csv文件
                return csv_loader(read_path)
            elif read_path.endswith("md"):  # 处理md文件
                return txt_loader(read_path)
            else:  # 不支持的文件类型，返回空列表
                return []

        # 获取指定数据目录下所有允许类型的文件路径列表
        allowed_files_path = listdir_with_allowed_type(
            get_abs_path(chroma_conf["data_path"]),  # 数据目录的绝对路径
            tuple(chroma_conf["allow_knowledge_file_type"])  # 允许的文件类型元组
        )

        # 遍历所有允许加载的文件路径
        for path in allowed_files_path:
            # 计算当前文件的MD5值，用于后续的重复检查
            md5_hex = get_file_md5_hex(path)

            if not md5_hex:  # 如果MD5计算失败，记录警告并跳过该文件
                logger.warning(f"[加载知识库] {path} MD5计算失败，跳过")
                continue

            if check_md5_hex(md5_hex):  # 如果该文件已加载过（MD5已存在），记录信息并跳过
                logger.info(f"[加载知识库] {path} 内容已经存在于知识库，跳过")
                continue

            try:
                # 根据文件类型加载文档，得到Document对象列表
                documents: list[Document] = get_file_documents(path)

                if not documents:  # 如果没有加载到有效内容，记录警告并跳过
                    logger.warning(f"[加载知识库] {path} 无有效文本内容，跳过")
                    continue

                # 使用文本分割器将文档分割为多个小片段
                split_document: list[Document] = self.spliter.split_documents(documents)

                if not split_document:  # 如果分割后无内容，记录警告并跳过
                    logger.warning(f"[加载知识库] {path} 分片后无内容，跳过")
                    continue

                # 将分割后的文档片段添加到向量存储中
                self.vector_store.add_documents(split_document)

                # 将当前文件的MD5值保存到存储文件，避免后续重复加载
                save_md5_hex(md5_hex)

                # 记录成功加载的日志
                logger.info(f"[加载知识库] {path} 内容加载成功")
            except Exception as e:
                # 捕获加载过程中的异常，记录错误日志（包含详细堆栈信息）
                logger.error(f"[加载知识库] {path} 加载失败：{str(e)}", exc_info=True)
                continue


# # 测试代码：当脚本直接运行时执行
# if __name__ == '__main__':
#     # 实例化向量存储服务
#     store = VectorStoreService()
#     # 加载文档到向量存储
#     store.load_document()
#     # 获取检索器
#     retriever = store.get_retriever()
#     # 调用检索器，查询与"迷路"相关的文档片段
#     res = retriever.invoke("迷路")
#     # 遍历检索结果，打印每个结果的内容和分隔线
#     for r in res:
#         print(r.page_content)
#         print("-" * 20)
