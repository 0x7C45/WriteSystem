"""
句式结构变异模块
Phase 3.2 - 打破模板句式，增加句式多样性
"""

import re
import random
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class SyntacticVariator:
    """句式结构变异处理器"""

    def __init__(self, knowledge_base: Dict):
        """
        初始化句式结构变异器

        Args:
            knowledge_base: 知识库字典，包含 sentence_starters, connector_variants 等
        """
        self.sentence_starters = knowledge_base.get("sentence_starters", {})
        self.connector_variants = knowledge_base.get("connector_variants", {})

        logger.info(
            f"句式结构变异器初始化: "
            f"{len(self.sentence_starters)} 种句首模式, "
            f"{len(self.connector_variants)} 种连接词变体"
        )

    def vary(self, text: str) -> str:
        """
        应用句式结构变异

        策略:
        1. 打散模板句（"首先-然后-接着-最后"）
        2. 句长随机化（5-50字混合）
        3. 句首多样化（10+种句首模式）
        4. 连接词替换

        Args:
            text: 原始文本

        Returns:
            变异后的文本
        """
        if not text.strip():
            return text

        logger.debug("应用句式结构变异")

        # 1. 打散模板连接词
        text = self._break_template_connectors(text)

        # 2. 句首多样化
        text = self._diversify_sentence_starters(text)

        # 3. 连接词替换
        text = self._replace_connectors(text)

        return text

    def _break_template_connectors(self, text: str) -> str:
        """
        打散模板化连接词序列

        识别并打破 "首先...然后...接着...最后..." 这类模板

        Args:
            text: 原始文本

        Returns:
            处理后的文本
        """
        # 定义常见模板连接词序列
        template_sequences = [
            ["首先", "然后", "接着", "最后"],
            ["首先", "其次", "再次", "最后"],
            ["第一", "第二", "第三", "第四"],
            ["一方面", "另一方面"],
        ]

        for sequence in template_sequences:
            # 检查是否存在完整序列
            all_present = all(conn in text for conn in sequence)

            if all_present:
                logger.debug(f"检测到模板序列: {sequence}")

                # 随机替换部分连接词
                for i, connector in enumerate(sequence):
                    if random.random() < 0.6:  # 60%概率替换
                        # 获取替代词
                        alternatives = self._get_connector_alternatives(connector)
                        if alternatives:
                            replacement = random.choice(alternatives)
                            text = text.replace(connector, replacement, 1)
                            logger.debug(f"替换: {connector} -> {replacement}")

        return text

    def _diversify_sentence_starters(self, text: str) -> str:
        """
        句首多样化

        将常见的句首模式替换为更多样的表达

        Args:
            text: 原始文本

        Returns:
            处理后的文本
        """
        if not self.sentence_starters:
            logger.warning("句首模式库为空，跳过句首多样化")
            return text

        # 按句子拆分
        sentences = self._split_sentences(text)

        modified_sentences = []
        for sent in sentences:
            # 检查句首是否匹配已知模式
            for pattern, alternatives in self.sentence_starters.items():
                if sent.startswith(pattern):
                    # 30%概率替换
                    if random.random() < 0.3 and alternatives:
                        replacement = random.choice(alternatives)
                        sent = replacement + sent[len(pattern):]
                        logger.debug(f"句首替换: {pattern} -> {replacement}")
                    break

            modified_sentences.append(sent)

        return "".join(modified_sentences)

    def _replace_connectors(self, text: str) -> str:
        """
        连接词替换

        将常见连接词替换为同义变体

        Args:
            text: 原始文本

        Returns:
            处理后的文本
        """
        if not self.connector_variants:
            logger.warning("连接词变体库为空，跳过连接词替换")
            return text

        for connector, variants in self.connector_variants.items():
            if connector in text and variants:
                # 查找所有出现位置
                positions = [m.start() for m in re.finditer(re.escape(connector), text)]

                # 随机替换部分出现（40%概率）
                num_to_replace = max(0, int(len(positions) * 0.4))
                if num_to_replace > 0:
                    replace_positions = random.sample(positions, num_to_replace)

                    # 从后向前替换
                    for pos in sorted(replace_positions, reverse=True):
                        replacement = random.choice(variants)
                        text = (
                            text[:pos] +
                            replacement +
                            text[pos + len(connector):]
                        )

        return text

    def _get_connector_alternatives(self, connector: str) -> List[str]:
        """
        获取连接词的替代词

        Args:
            connector: 原连接词

        Returns:
            替代词列表
        """
        # 预定义替代词映射
        alternatives_map = {
            "首先": ["起初", "最初", "一开始", "率先"],
            "然后": ["随后", "接着", "之后", "继而"],
            "接着": ["紧接着", "随之", "其后", "进而"],
            "最后": ["最终", "终于", "最末", "末了"],
            "其次": ["第二", "再者", "另外"],
            "再次": ["第三", "又", "再者"],
            "第一": ["首要的是", "第一点"],
            "第二": ["其次", "第二点"],
            "一方面": ["从一个角度看", "一个方面"],
            "另一方面": ["从另一个角度看", "另一个方面"],
        }

        return alternatives_map.get(connector, [])

    def _split_sentences(self, text: str) -> List[str]:
        """
        拆分句子（保留标点）

        Args:
            text: 文本

        Returns:
            句子列表
        """
        # 按句号、问号、感叹号拆分，但保留标点
        pattern = r'([。！？])'
        parts = re.split(pattern, text)

        # 重新组合句子和标点
        sentences = []
        for i in range(0, len(parts) - 1, 2):
            if i + 1 < len(parts):
                sentences.append(parts[i] + parts[i + 1])

        # 处理最后一个片段（如果没有标点结尾）
        if len(parts) % 2 == 1 and parts[-1].strip():
            sentences.append(parts[-1])

        return sentences

    def analyze_sentence_patterns(self, text: str) -> Dict:
        """
        分析句式模式

        Args:
            text: 文本

        Returns:
            {
                "total_sentences": int,
                "avg_length": float,
                "length_variance": float,
                "template_sequences_found": list,
                "starter_patterns": dict
            }
        """
        sentences = self._split_sentences(text)

        # 句长统计
        lengths = [len(s) for s in sentences if s.strip()]
        avg_length = sum(lengths) / len(lengths) if lengths else 0
        variance = sum((x - avg_length) ** 2 for x in lengths) / len(lengths) if lengths else 0

        # 检测模板序列
        template_sequences_found = []
        template_sequences = [
            ["首先", "然后", "接着", "最后"],
            ["首先", "其次", "再次", "最后"],
        ]

        for sequence in template_sequences:
            if all(any(conn in s for s in sentences) for conn in sequence):
                template_sequences_found.append(sequence)

        # 句首模式统计
        starter_patterns = {}
        for sent in sentences:
            for pattern in self.sentence_starters.keys():
                if sent.startswith(pattern):
                    starter_patterns[pattern] = starter_patterns.get(pattern, 0) + 1

        return {
            "total_sentences": len(sentences),
            "avg_length": avg_length,
            "length_variance": variance,
            "min_length": min(lengths) if lengths else 0,
            "max_length": max(lengths) if lengths else 0,
            "template_sequences_found": template_sequences_found,
            "starter_patterns": starter_patterns
        }

    def vary_with_analysis(self, text: str) -> Dict:
        """
        应用句式变异并返回分析报告

        Args:
            text: 原始文本

        Returns:
            {
                "original": str,
                "varied": str,
                "original_analysis": dict,
                "varied_analysis": dict
            }
        """
        # 原始分析
        original_analysis = self.analyze_sentence_patterns(text)

        # 应用变异
        varied = self.vary(text)

        # 变异后分析
        varied_analysis = self.analyze_sentence_patterns(varied)

        return {
            "original": text,
            "varied": varied,
            "original_analysis": original_analysis,
            "varied_analysis": varied_analysis
        }
