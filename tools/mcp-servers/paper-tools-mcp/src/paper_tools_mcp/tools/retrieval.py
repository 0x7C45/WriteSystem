"""检索工具：滑动窗口切片 + all-MiniLM-L6-v2 无状态检索、query_data_facts。"""

import re
from pathlib import Path

import numpy as np

# ── 滑动窗口切片 ──────────────────────────────────────


def sliding_window_chunk(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[str]:
    """按滑动窗口切分文本为块。

    Args:
        text: 输入文本。
        chunk_size: 每块目标字符数。
        overlap: 块间重叠字符数。
    """
    if not text.strip():
        return []

    # 按自然段分割，保持段落完整性
    paragraphs = text.split('\n')
    chunks: list[str] = []
    current_chunk: list[str] = []
    current_length = 0

    for para in paragraphs:
        para_len = len(para)

        if current_length + para_len > chunk_size and current_chunk:
            chunks.append('\n'.join(current_chunk))

            # 保留重叠部分
            overlap_text = []
            overlap_length = 0
            for p in reversed(current_chunk):
                if overlap_length + len(p) > overlap:
                    break
                overlap_text.insert(0, p)
                overlap_length += len(p)

            current_chunk = overlap_text
            current_length = overlap_length

        current_chunk.append(para)
        current_length += para_len + 1  # +1 for newline

    if current_chunk:
        chunks.append('\n'.join(current_chunk))

    return chunks


# ── Embedding 模型（懒加载） ──────────────────────────

_embedding_model = None
_embedding_tokenizer = None


def _get_embedding_model():
    """懒加载 all-MiniLM-L6-v2 模型。"""
    global _embedding_model, _embedding_tokenizer
    if _embedding_model is not None:
        return _embedding_model, _embedding_tokenizer

    from sentence_transformers import SentenceTransformer

    _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    _embedding_tokenizer = None  # model 内置 tokenizer
    return _embedding_model, _embedding_tokenizer


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """计算向量 a 和矩阵 b 的余弦相似度。"""
    a_norm = a / (np.linalg.norm(a) + 1e-8)
    b_norm = b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-8)
    return b_norm @ a_norm


# ── search_blocks ──────────────────────────────────────


def search_blocks(
    query: str,
    source_files: list[str],
    top_k: int = 3,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> dict:
    """滑动窗口切片 + all-MiniLM-L6-v2 无状态检索。

    Args:
        query: 查询文本（通常是当前章节的极细骨架）。
        source_files: 要检索的源文件路径列表。
        top_k: 返回最相关的 K 个文本块。
        chunk_size: 切片大小（字符数）。
        chunk_overlap: 切片重叠（字符数）。
    """
    # 收集所有文本块
    all_chunks: list[dict] = []

    for file_path in source_files:
        path = Path(file_path)
        if not path.exists():
            continue

        text = path.read_text(encoding='utf-8')
        chunks = sliding_window_chunk(text, chunk_size=chunk_size, overlap=chunk_overlap)

        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "text": chunk,
                "source": file_path,
                "chunk_index": i,
            })

    if not all_chunks:
        return {"query": query, "results": [], "total_chunks": 0}

    # 编码
    try:
        model, _ = _get_embedding_model()
        query_embedding = model.encode([query])[0]
        chunk_texts = [c["text"] for c in all_chunks]
        chunk_embeddings = model.encode(chunk_texts)

        similarities = _cosine_similarity(query_embedding, chunk_embeddings)

        # Top-K
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score > 0.1:  # 最低相关度阈值
                results.append({
                    "text": all_chunks[idx]["text"],
                    "source": all_chunks[idx]["source"],
                    "score": round(score, 4),
                    "chunk_index": all_chunks[idx]["chunk_index"],
                })

    except Exception as e:
        # Embedding 模型不可用时，退化为关键词匹配
        query_lower = query.lower()
        results = []
        for chunk in all_chunks:
            score = sum(1 for word in query_lower if word in chunk["text"].lower())
            if score > 0:
                results.append({
                    "text": chunk["text"],
                    "source": chunk["source"],
                    "score": score / len(query_lower),
                    "chunk_index": chunk["chunk_index"],
                })
        results.sort(key=lambda x: x["score"], reverse=True)
        results = results[:top_k]

    return {
        "query": query,
        "results": results,
        "total_chunks": len(all_chunks),
    }


# ── query_data_facts ──────────────────────────────────


def query_data_facts(
    query: str,
    data_file: str = "02_工作素材/数据与分析/data_facts.md",
) -> dict:
    """按关键词检索 data_facts.md 中的数据段落。

    Args:
        query: 查询关键词（如"信度检验"、"回归分析"）。
        data_file: data_facts.md 文件路径。
    """
    path = Path(data_file)
    if not path.exists():
        return {"error": f"数据文件不存在: {data_file}"}

    text = path.read_text(encoding='utf-8')

    # 按二级标题切分为段落
    sections = re.split(r'\n(?=## )', text)

    # 关键词匹配
    keywords = query.lower().split()
    results: list[dict] = []

    for section in sections:
        if not section.strip():
            continue

        section_lower = section.lower()

        # 计算匹配度
        match_count = sum(1 for kw in keywords if kw in section_lower)
        if match_count == 0:
            continue

        relevance = match_count / len(keywords)

        # 提取标题
        title_match = re.match(r'##\s+(.+)', section)
        title = title_match.group(1).strip() if title_match else "（无标题）"

        results.append({
            "title": title,
            "content": section.strip(),
            "relevance": round(relevance, 2),
            "match_count": match_count,
        })

    # 按匹配度排序
    results.sort(key=lambda x: x["relevance"], reverse=True)

    if not results:
        return {
            "query": query,
            "data_file": data_file,
            "results": [],
            "warning": "未找到匹配数据，请确认关键词或检查 data_facts.md",
        }

    return {
        "query": query,
        "data_file": data_file,
        "results": results,
        "match_count": len(results),
    }
