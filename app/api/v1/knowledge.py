import os
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.response import ResponseModel
from utils.path_tools import get_abs_path
from utils.config_handler import chroma_conf
from utils.file_handler import get_file_md5_hex

router = APIRouter()


def get_data_path():
    """获取数据目录路径"""
    return get_abs_path(chroma_conf["data_path"])


def get_md5_store_path():
    """获取MD5存储文件路径"""
    return get_abs_path(chroma_conf["md5_hex_store"])


def get_vectorized_md5_list() -> List[str]:
    """获取已向量化文件的MD5列表"""
    md5_path = get_md5_store_path()
    if not os.path.exists(md5_path):
        return []
    with open(md5_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]


@router.get("/files", response_model=ResponseModel, summary="获取知识库文件列表")
async def get_knowledge_files(current_user: User = Depends(get_current_user)):
    """获取data目录下的知识库文件列表"""
    data_path = get_data_path()

    if not os.path.exists(data_path):
        return ResponseModel(code=200, message="success", data={"files": [], "vectorized_count": 0, "total_count": 0})

    # 获取已向量化的 MD5 列表
    vectorized_md5_list = get_vectorized_md5_list()

    # 允许的文件类型
    allowed_types = tuple(chroma_conf.get("allow_knowledge_file_type", ["txt", "pdf", "csv","md"]))

    files = []
    for filename in os.listdir(data_path):
        filepath = os.path.join(data_path, filename)

        # 跳过目录
        if os.path.isdir(filepath):
            continue

        # 检查文件类型
        ext = filename.split('.')[-1].lower() if '.' in filename else ''
        if ext not in allowed_types:
            continue

        # 获取文件信息
        stat = os.stat(filepath)
        md5 = get_file_md5_hex(filepath) or ""
        is_vectorized = md5 in vectorized_md5_list if md5 else False

        files.append({
            "name": filename,
            "size": stat.st_size,
            "modified_time": stat.st_mtime,
            "md5": md5,
            "is_vectorized": is_vectorized,
            "type": '.' + ext if ext else ''
        })

    # 按修改时间排序
    files.sort(key=lambda x: x["modified_time"], reverse=True)

    vectorized_count = sum(1 for f in files if f["is_vectorized"])

    return ResponseModel(
        code=200,
        message="success",
        data={
            "files": files,
            "total_count": len(files),
            "vectorized_count": vectorized_count
        }
    )


@router.post("/upload", response_model=ResponseModel, summary="上传知识库文件")
async def upload_knowledge_file(
        file: UploadFile = File(...),
        current_user: User = Depends(get_current_user)
):
    """上传文件到data目录"""
    # 检查文件类型
    allowed_types = tuple(chroma_conf.get("allow_knowledge_file_type", ["txt", "pdf", "csv","md"]))
    ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    if ext not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型，仅支持: {', '.join(allowed_types)}"
        )
    data_path = get_data_path()
    # 确保目录存在
    os.makedirs(data_path, exist_ok=True)
    # 保存文件
    filepath = os.path.join(data_path, file.filename)

    try:
        with open(filepath, "wb") as f:
            content = await file.read()
            f.write(content)

        # 获取文件信息
        stat = os.stat(filepath)
        md5 = get_file_md5_hex(filepath) or ""

        return ResponseModel(
            code=200,
            message="上传成功",
            data={
                "file": {
                    "name": file.filename,
                    "size": stat.st_size,
                    "md5": md5,
                    "is_vectorized": False
                }
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


def remove_md5_from_store(md5_to_remove: str):
    """从MD5存储文件中删除指定的MD5"""
    md5_path = get_md5_store_path()
    if not os.path.exists(md5_path):
        return

    # 读取所有 MD5
    with open(md5_path, "r", encoding="utf-8") as f:
        md5_list = [line.strip() for line in f.readlines() if line.strip()]

    # 过滤掉要删除的 MD5
    md5_list = [md5 for md5 in md5_list if md5 != md5_to_remove]

    # 重新写入
    with open(md5_path, "w", encoding="utf-8") as f:
        for md5 in md5_list:
            f.write(md5 + "\n")


import os
from langchain_chroma import Chroma


# 注意：这里不再需要导入 embed_model，节省资源

def delete_vectors_by_source(filepath: str) -> int:
    """
    从向量数据库中删除指定文件的向量数据
    优化点：
    1. 不加载 Embedding 模型（仅做元数据操作）。
    2. 尝试多种路径格式（绝对/相对）以防止路径不匹配导致的删除失败。
    3. 直接使用 delete(where=...) 避免先查询后删除。
    """
    try:
        chroma_path = get_abs_path(chroma_conf.get("persist_directory", "chroma_db"))

        # 1. 初始化 Chroma，不传入 embedding_function，避免加载模型
        #    注意：仅进行元数据/ID操作时，embedding_function 可以为 None
        vector_store = Chroma(
            collection_name=chroma_conf["collection_name"],
            embedding_function=None,  # 关键优化
            persist_directory=chroma_path,
        )

        # 获取原生 collection 对象
        collection = vector_store._collection

        # 2. 路径标准化处理 (解决路径不匹配问题)
        abs_path = os.path.abspath(filepath)
        rel_path = os.path.relpath(filepath, start=os.getcwd())  # 或者相对于项目根目录
        deleted_count = 0
        # 3. 直接通过 where 删除 (原子操作)
        # 尝试删除绝对路径匹配项
        try:
            # 检查绝对路径
            target_ids = []
            results_abs = collection.get(where={"source": abs_path})
            if results_abs and results_abs['ids']:
                target_ids.extend(results_abs['ids'])

            # 检查相对路径 (防止入库时存的是相对路径)
            if rel_path != abs_path:
                results_rel = collection.get(where={"source": rel_path})
                if results_rel and results_rel['ids']:
                    target_ids.extend(results_rel['ids'])

            # 去重 ID
            target_ids = list(set(target_ids))

            if target_ids:
                collection.delete(ids=target_ids)
                deleted_count = len(target_ids)
                print(f"已删除向量数据: {deleted_count} 条 (Source: {filepath})")
            else:
                print(f"未找到相关向量数据: {filepath}")

        except Exception as e:
            print(f"执行删除操作失败: {e}")

        return deleted_count

    except Exception as e:
        print(f"连接向量库失败: {str(e)}")
        return 0


@router.delete("/files/{filename}", response_model=ResponseModel, summary="删除知识库文件")
async def delete_knowledge_file(
        filename: str,
        current_user: User = Depends(get_current_user)
):
    """删除指定的知识库文件，同时删除对应的向量数据和MD5记录"""
    data_path = get_data_path()
    filepath = os.path.join(data_path, filename)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="文件不存在")

    try:
        # 1. 先获取文件的 MD5
        file_md5 = get_file_md5_hex(filepath) or ""

        # 2. 删除向量数据库中的数据
        deleted_vectors = delete_vectors_by_source(filepath)

        # 3. 从 MD5 存储文件中删除记录
        if file_md5:
            remove_md5_from_store(file_md5)

        # 4. 删除文件
        os.remove(filepath)

        return ResponseModel(
            code=200,
            message="删除成功",
            data={"deleted_vectors": deleted_vectors}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.post("/vectorize", response_model=ResponseModel, summary="向量化知识库")
async def vectorize_knowledge(current_user: User = Depends(get_current_user)):
    """执行知识库向量化"""
    try:
        from rag.vector_store import VectorStoreService

        # 创建向量存储服务并加载文档
        vs = VectorStoreService()
        vs.load_document()

        # 获取更新后的统计
        vectorized_md5_list = get_vectorized_md5_list()

        return ResponseModel(
            code=200,
            message="向量化完成",
            data={"vectorized_count": len(vectorized_md5_list)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"向量化失败: {str(e)}")


@router.get("/stats", response_model=ResponseModel, summary="获取知识库统计")
async def get_knowledge_stats(current_user: User = Depends(get_current_user)):
    """获取知识库统计信息"""
    data_path = get_data_path()
    chroma_path = get_abs_path(chroma_conf.get("persist_directory", "chroma_db"))

    # 文件统计
    file_count = 0
    total_size = 0
    allowed_types = tuple(chroma_conf.get("allow_knowledge_file_type", ["txt", "pdf", "csv","md"]))

    if os.path.exists(data_path):
        for filename in os.listdir(data_path):
            filepath = os.path.join(data_path, filename)
            ext = filename.split('.')[-1].lower() if '.' in filename else ''
            if os.path.isfile(filepath) and ext in allowed_types:
                file_count += 1
                total_size += os.path.getsize(filepath)

    # 向量化统计
    vectorized_count = len(get_vectorized_md5_list())

    # 向量库大小
    chroma_size = 0
    if os.path.exists(chroma_path):
        for dirpath, dirnames, filenames in os.walk(chroma_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                chroma_size += os.path.getsize(fp)

    return ResponseModel(
        code=200,
        message="success",
        data={
            "file_count": file_count,
            "total_size": total_size,
            "vectorized_count": vectorized_count,
            "chroma_size": chroma_size,
        }
    )

@router.post("/optimize", response_model=ResponseModel, summary="优化向量数据库")
async def optimize_vector_db(current_user: User = Depends(get_current_user)):
    """优化向量数据库，压缩释放空间"""
    try:
        import sqlite3
        chroma_path = get_abs_path(chroma_conf.get("persist_directory", "chroma_db"))

        # 找到 chroma.sqlite3 文件
        sqlite_path = os.path.join(chroma_path, "chroma.sqlite3")

        if os.path.exists(sqlite_path):
            # 执行 VACUUM 压缩数据库
            conn = sqlite3.connect(sqlite_path)
            conn.execute("VACUUM")
            conn.close()

            # 获取优化后的大小
            new_size = 0
            for dirpath, dirnames, filenames in os.walk(chroma_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    new_size += os.path.getsize(fp)

            return ResponseModel(
                code=200,
                message="优化完成",
                data={"new_size": new_size}
            )
        else:
            return ResponseModel(code=200, message="数据库文件不存在", data=None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"优化失败: {str(e)}")
