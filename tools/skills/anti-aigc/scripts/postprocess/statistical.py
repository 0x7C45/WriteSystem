"""
统计特征多样化模块
Phase 3.1 - 通过同义词替换和统计特征调整降低AI检测分数
"""

import json
import random
import re
from typing import Dict, List, Set, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class StatisticalDiversifier:
    """统计特征多样化处理器"""

    def __init__(self, knowledge_base: Dict):
        """
        初始化统计特征多样化器

        Args:
            knowledge_base: 知识库字典，包含 synonym_dict 等
        """
        self.synonym_dict = knowledge_base.get("synonym_dict", {})
        self.ai_patterns = knowledge_base.get("ai_patterns", {})

        logger.info(
            f"统计特征多样化器初始化: "
            f"{len(self.synonym_dict)} 个同义词组"
        )

    def diversify(self, text: str, coverage: float = 0.65) -> str:
        """
        应用统计特征多样化

        策略:
        1. 识别高频虚词（"的"、"是"、"在"等）
        2. 按覆盖率随机替换为同义词
        3. 保留30%原始表达，避免过度修改

        Args:
            text: 原始文本
            coverage: 替换覆盖率 (0.6-0.7 推荐)

        Returns:
            多样化后的文本
        """
        if not text.strip():
            return text

        logger.debug(f"应用统计特征多样化 (覆盖率: {coverage:.1%})")

        # 1. 同义词替换
        text = self._apply_synonym_replacement(text, coverage)

        # 2. 标点符号多样化
        text = self._diversify_punctuation(text)

        return text

    def _apply_synonym_replacement(self, text: str, coverage: float) -> str:
        """
        应用同义词替换

        Args:
            text: 原始文本
            coverage: 替换覆盖率

        Returns:
            替换后的文本
        """
        if not self.synonym_dict:
            logger.warning("同义词词典为空，跳过同义词替换")
            return text

        # 遍历同义词字典
        for word, synonyms in self.synonym_dict.items():
            if not synonyms or not isinstance(synonyms, list):
                continue

            # 查找该词在文本中的所有位置
            pattern = re.compile(re.escape(word))
            matches = list(pattern.finditer(text))

            if not matches:
                continue

            # 根据覆盖率决定替换哪些出现
            num_to_replace = max(1, int(len(matches) * coverage))
            positions_to_replace = random.sample(range(len(matches)), num_to_replace)

            # 从后向前替换（避免位置偏移）
            for i in sorted(positions_to_replace, reverse=True):
                match = matches[i]
                replacement = random.choice(synonyms)

                # 执行替换
                text = (
                    text[:match.start()] +
                    replacement +
                    text[match.end():]
                )

        return text

    def _diversify_punctuation(self, text: str) -> str:
        """
        标点符号多样化

        策略:
        - 部分逗号替换为分号
        - 部分句号替换为感叹号（在适当语境）

        Args:
            text: 原始文本

        Returns:
            多样化后的文本
        """
        # 识别可替换的逗号（前后有足够长的句子片段）
        # 10%的逗号替换为分号
        comma_positions = [m.start() for m in re.finditer('，', text)]
        num_to_replace = max(0, int(len(comma_positions) * 0.1))

        if num_to_replace > 0:
            positions = random.sample(comma_positions, num_to_replace)
            for pos in sorted(positions, reverse=True):
                text = text[:pos] + '；' + text[pos+1:]

        return text

    def smooth_word_frequency(self, text: str) -> Dict[str, int]:
        """
        分析并平滑词频分布

        Args:
            text: 文本

        Returns:
            词频统计
        """
        # 分词（简化实现，实际需要使用 jieba 等分词工具）
        words = re.findall(r'[一-鿿]+', text)

        # 统计词频
        freq = {}
        for word in words:
            freq[word] = freq.get(word, 0) + 1

        return freq

    def calculate_sentence_length_variance(self, text: str) -> Dict:
        """
        计算句长方差

        Args:
            text: 文本

        Returns:
            {
                "lengths": list,
                "mean": float,
                "variance": float
            }
        """
        # 按句号、问号、感叹号拆分句子
        sentences = re.split('[。！？]', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        lengths = [len(s) for s in sentences]

        if not lengths:
            return {"lengths": [], "mean": 0, "variance": 0}

        mean = sum(lengths) / len(lengths)
        variance = sum((x - mean) ** 2 for x in lengths) / len(lengths)

        return {
            "lengths": lengths,
            "mean": mean,
            "variance": variance,
            "min": min(lengths),
            "max": max(lengths)
        }

    def identify_ai_patterns(self, text: str) -> List[Dict]:
        """
        识别AI高频模式

        Args:
            text: 待检测文本

        Returns:
            检测到的AI模式列表
        """
        detected_patterns = []

        if not self.ai_patterns:
            return detected_patterns

        # 检测高频虚词模式
        ai_phrases = self.ai_patterns.get("high_frequency_phrases", [])
        for phrase in ai_phrases:
            if phrase in text:
                count = text.count(phrase)
                detected_patterns.append({
                    "type": "high_frequency_phrase",
                    "pattern": phrase,
                    "count": count
                })

        # 检测模板化连接词
        template_connectors = self.ai_patterns.get("template_connectors", [])
        for connector in template_connectors:
            if connector in text:
                detected_patterns.append({
                    "type": "template_connector",
                    "pattern": connector
                })

        return detected_patterns

    def diversify_with_analysis(self, text: str, coverage: float = 0.65) -> Dict:
        """
        应用多样化并返回分析报告

        Args:
            text: 原始文本
            coverage: 替换覆盖率

        Returns:
            {
                "original": str,
                "diversified": str,
                "statistics": dict,
                "patterns_removed": list
            }
        """
        # 原始文本分析
        original_stats = {
            "sentence_lengths": self.calculate_sentence_length_variance(text),
            "ai_patterns": self.identify_ai_patterns(text)
        }

        # 应用多样化
        diversified = self.diversify(text, coverage)

        # 多样化后分析
        diversified_stats = {
            "sentence_lengths": self.calculate_sentence_length_variance(diversified),
            "ai_patterns": self.identify_ai_patterns(diversified)
        }

        # 计算改进
        patterns_removed = len(original_stats["ai_patterns"]) - len(diversified_stats["ai_patterns"])

        return {
            "original": text,
            "diversified": diversified,
            "original_statistics": original_stats,
            "diversified_statistics": diversified_stats,
            "patterns_removed": patterns_removed
        }
