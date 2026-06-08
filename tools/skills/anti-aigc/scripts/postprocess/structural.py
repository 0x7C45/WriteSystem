"""
结构重组模块
Phase 3.3 - 打破总-分-总结构，注入人类不完美特征
"""

import re
import random
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class StructuralReorganizer:
    """结构重组处理器"""

    def __init__(self, knowledge_base: Dict):
        """
        初始化结构重组器

        Args:
            knowledge_base: 知识库字典
        """
        self.knowledge_base = knowledge_base

        # 限定词库
        self.hedging_words = [
            "可能", "或许", "大概", "似乎", "看起来",
            "在一定程度上", "某种意义上", "相对而言",
            "一般来说", "通常情况下", "基本上"
        ]

        # 不确定性表达
        self.uncertainty_phrases = [
            "需要进一步研究", "尚待探讨", "有待验证",
            "仍存在争议", "并非绝对", "也存在例外"
        ]

        logger.info("结构重组器初始化完成")

    def reorganize(self, text: str, aggressive: bool = False) -> str:
        """
        应用结构重组

        策略:
        1. 打破"总-分-总"论证结构
        2. 段落融合/拆分
        3. 论据重排
        4. 注入"人类不完美"（限定词、不确定性）

        Args:
            text: 原始文本
            aggressive: 是否使用激进模式（更大幅度重组）

        Returns:
            重组后的文本
        """
        if not text.strip():
            return text

        logger.debug(f"应用结构重组 (激进模式: {aggressive})")

        # 1. 注入限定词
        text = self._inject_hedging(text)

        # 2. 注入不确定性表达
        text = self._inject_uncertainty(text)

        # 3. 打破过度完美的结构
        if aggressive:
            text = self._break_perfect_structure(text)

        return text

    def _inject_hedging(self, text: str) -> str:
        """
        注入限定词

        在断言性强的句子中添加限定词，弱化绝对性

        Args:
            text: 原始文本

        Returns:
            处理后的文本
        """
        # 识别断言性强的模式
        assertive_patterns = [
            (r'(是|为)([^，。！？]{1,20}的)', r'\1\2'),  # "是...的"
            (r'(必须|一定|肯定)', r'\1'),
            (r'(证明|表明|说明)([^，。！？]{5,})', r'\1\2'),
        ]

        sentences = self._split_sentences(text)
        modified_sentences = []

        for sent in sentences:
            # 检测是否包含断言性表达
            has_assertion = any(
                re.search(pattern, sent) for pattern, _ in assertive_patterns
            )

            # 如果有断言且句子较短，30%概率添加限定词
            if has_assertion and len(sent) < 50 and random.random() < 0.3:
                # 选择合适的限定词
                hedging = random.choice(self.hedging_words)

                # 在句首或适当位置插入
                if sent.startswith(("这", "该", "此")):
                    # 在主语后插入
                    sent = re.sub(r'^(这|该|此)([^，。]{2,})', rf'\1\2{hedging}', sent)
                else:
                    # 在句首插入
                    sent = hedging + sent

                logger.debug(f"注入限定词: {hedging}")

            modified_sentences.append(sent)

        return "".join(modified_sentences)

    def _inject_uncertainty(self, text: str) -> str:
        """
        注入不确定性表达

        在结论性句子后添加不确定性表达

        Args:
            text: 原始文本

        Returns:
            处理后的文本
        """
        # 识别结论性句子（通常以"因此"、"所以"、"综上"开头）
        conclusion_patterns = [
            "因此", "所以", "综上", "总之", "由此可见", "可以看出"
        ]

        sentences = self._split_sentences(text)
        modified_sentences = []

        for i, sent in enumerate(sentences):
            modified_sentences.append(sent)

            # 检测是否为结论性句子
            is_conclusion = any(sent.startswith(pattern) for pattern in conclusion_patterns)

            # 20%概率在结论后添加不确定性表达
            if is_conclusion and random.random() < 0.2:
                uncertainty = random.choice(self.uncertainty_phrases)
                # 在句子后添加（注意标点）
                modified_sentences[-1] = sent.rstrip('。') + f"，但{uncertainty}。"
                logger.debug(f"注入不确定性: {uncertainty}")

        return "".join(modified_sentences)

    def _break_perfect_structure(self, text: str) -> str:
        """
        打破过度完美的结构

        Args:
            text: 原始文本

        Returns:
            处理后的文本
        """
        # 检测是否有明显的总-分-总结构
        if self._has_perfect_structure(text):
            logger.debug("检测到总-分-总结构，打破中...")

            # 策略: 移除或弱化总起句
            sentences = self._split_sentences(text)

            if len(sentences) > 3:
                # 检测第一句是否为总起句
                first_sent = sentences[0]
                if self._is_opening_sentence(first_sent):
                    # 50%概率移除总起句
                    if random.random() < 0.5:
                        sentences = sentences[1:]
                        logger.debug("移除总起句")

        return "".join(sentences) if 'sentences' in locals() else text

    def _has_perfect_structure(self, text: str) -> bool:
        """
        检测是否有总-分-总结构

        Args:
            text: 文本

        Returns:
            是否有该结构
        """
        # 简化检测：是否同时有总起和总结标志
        opening_markers = ["首先", "本文", "本段", "以下"]
        conclusion_markers = ["综上", "总之", "总而言之", "由此可见"]

        has_opening = any(marker in text[:50] for marker in opening_markers)
        has_conclusion = any(marker in text[-100:] for marker in conclusion_markers)

        return has_opening and has_conclusion

    def _is_opening_sentence(self, sentence: str) -> bool:
        """
        判断是否为总起句

        Args:
            sentence: 句子

        Returns:
            是否为总起句
        """
        opening_patterns = [
            "本文", "本段", "本节", "以下", "下面",
            "首先", "第一", "主要"
        ]

        return any(sentence.startswith(pattern) for pattern in opening_patterns)

    def _split_sentences(self, text: str) -> List[str]:
        """
        拆分句子（保留标点）

        Args:
            text: 文本

        Returns:
            句子列表
        """
        pattern = r'([。！？])'
        parts = re.split(pattern, text)

        sentences = []
        for i in range(0, len(parts) - 1, 2):
            if i + 1 < len(parts):
                sentences.append(parts[i] + parts[i + 1])

        if len(parts) % 2 == 1 and parts[-1].strip():
            sentences.append(parts[-1])

        return sentences

    def analyze_structure(self, text: str) -> Dict:
        """
        分析段落结构

        Args:
            text: 文本

        Returns:
            {
                "has_perfect_structure": bool,
                "hedging_words_count": int,
                "uncertainty_phrases_count": int,
                "assertive_sentences": int,
                "total_sentences": int
            }
        """
        sentences = self._split_sentences(text)

        # 检测限定词数量
        hedging_count = sum(
            1 for word in self.hedging_words if word in text
        )

        # 检测不确定性表达数量
        uncertainty_count = sum(
            1 for phrase in self.uncertainty_phrases if phrase in text
        )

        # 检测断言性句子
        assertive_patterns = [
            "必须", "一定", "肯定", "毫无疑问", "显然", "当然"
        ]
        assertive_count = sum(
            1 for sent in sentences
            if any(pattern in sent for pattern in assertive_patterns)
        )

        return {
            "has_perfect_structure": self._has_perfect_structure(text),
            "hedging_words_count": hedging_count,
            "uncertainty_phrases_count": uncertainty_count,
            "assertive_sentences": assertive_count,
            "total_sentences": len(sentences),
            "hedging_ratio": hedging_count / len(sentences) if sentences else 0
        }

    def reorganize_with_analysis(self, text: str, aggressive: bool = False) -> Dict:
        """
        应用结构重组并返回分析报告

        Args:
            text: 原始文本
            aggressive: 是否使用激进模式

        Returns:
            {
                "original": str,
                "reorganized": str,
                "original_analysis": dict,
                "reorganized_analysis": dict
            }
        """
        # 原始分析
        original_analysis = self.analyze_structure(text)

        # 应用重组
        reorganized = self.reorganize(text, aggressive)

        # 重组后分析
        reorganized_analysis = self.analyze_structure(reorganized)

        return {
            "original": text,
            "reorganized": reorganized,
            "original_analysis": original_analysis,
            "reorganized_analysis": reorganized_analysis
        }
