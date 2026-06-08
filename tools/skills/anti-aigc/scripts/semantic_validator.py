"""
语义相似度验证器

使用 sentence-transformers 计算语义向量和余弦相似度
"""

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


class SemanticValidator:
    """语义相似度验证器"""

    def __init__(self, model_name: str = "paraphrase-multilingual-mpnet-base-v2"):
        """
        初始化语义验证器

        Args:
            model_name: sentence-transformers模型名称
                - paraphrase-multilingual-mpnet-base-v2: 多语言模型（推荐）
                - paraphrase-MiniLM-L6-v2: 轻量英文模型
                - distiluse-base-multilingual-cased-v2: 多语言轻量模型
        """
        logger.info(f"加载语义模型: {model_name}")
        self.model = SentenceTransformer(model_name)
        logger.info("语义模型加载完成")

    def check_fidelity(self, original: str, modified: str) -> float:
        """
        计算两段文本的语义相似度

        Args:
            original: 原始文本
            modified: 修改后文本

        Returns:
            相似度分数 (0-1)，越接近1表示语义越相似
        """
        if not original.strip() or not modified.strip():
            logger.warning("输入文本为空，返回相似度0")
            return 0.0

        # 计算语义向量
        embeddings = self.model.encode([original, modified])

        # 计算余弦相似度
        similarity = cosine_similarity(
            [embeddings[0]],
            [embeddings[1]]
        )[0][0]

        return float(similarity)

    def batch_check(self, pairs: List[Tuple[str, str]]) -> List[float]:
        """
        批量检查文本对的语义相似度

        Args:
            pairs: 文本对列表，每个元素为 (original, modified) 元组

        Returns:
            相似度分数列表
        """
        if not pairs:
            return []

        logger.info(f"批量计算 {len(pairs)} 对文本的语义相似度")

        # 分别提取原始文本和修改后文本
        originals = [p[0] for p in pairs]
        modifieds = [p[1] for p in pairs]

        # 批量编码
        original_embeddings = self.model.encode(originals)
        modified_embeddings = self.model.encode(modifieds)

        # 计算每对文本的相似度
        similarities = []
        for i in range(len(pairs)):
            sim = cosine_similarity(
                [original_embeddings[i]],
                [modified_embeddings[i]]
            )[0][0]
            similarities.append(float(sim))

        logger.info(f"批量计算完成，平均相似度: {np.mean(similarities):.3f}")
        return similarities

    def validate_threshold(
        self,
        original: str,
        modified: str,
        threshold: float = 0.85
    ) -> Tuple[bool, float]:
        """
        验证修改后文本是否满足语义保真度阈值

        Args:
            original: 原始文本
            modified: 修改后文本
            threshold: 相似度阈值 (默认0.85)

        Returns:
            (是否通过, 相似度分数)
        """
        similarity = self.check_fidelity(original, modified)
        passed = similarity >= threshold

        if not passed:
            logger.warning(
                f"语义保真度未达标: {similarity:.3f} < {threshold:.3f}"
            )

        return passed, similarity

    def compare_multiple(
        self,
        original: str,
        candidates: List[str]
    ) -> List[Tuple[int, float]]:
        """
        比较原始文本与多个候选文本的相似度，返回排序结果

        Args:
            original: 原始文本
            candidates: 候选文本列表

        Returns:
            排序后的 (索引, 相似度) 列表，按相似度降序
        """
        if not candidates:
            return []

        # 计算原始文本的向量
        original_embedding = self.model.encode([original])[0]

        # 计算所有候选文本的向量
        candidate_embeddings = self.model.encode(candidates)

        # 计算相似度
        similarities = []
        for i, candidate_embedding in enumerate(candidate_embeddings):
            sim = cosine_similarity(
                [original_embedding],
                [candidate_embedding]
            )[0][0]
            similarities.append((i, float(sim)))

        # 按相似度降序排序
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities
