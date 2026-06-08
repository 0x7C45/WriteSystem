"""
引用完整性验证器

验证文本改写前后引用标记的完整性
"""

import re
from typing import Set, Dict, List, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class CitationValidator:
    """引用完整性验证器"""

    def __init__(self, citation_registry_path: str = None):
        """
        初始化引用验证器

        Args:
            citation_registry_path: 引用注册表路径（可选）
                如: "05_撰写过程/_引用编号注册表.md"
        """
        self.registry = set()

        if citation_registry_path:
            self.registry = self._load_registry(citation_registry_path)
            logger.info(f"加载引用注册表: {len(self.registry)} 个引用")

    def _load_registry(self, path: str) -> Set[str]:
        """
        从注册表文件加载已知引用

        Args:
            path: 注册表文件路径

        Returns:
            引用ID集合
        """
        registry = set()

        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 从注册表中提取所有引用标记
            # 格式: [Author_Year] 或 [Author_Year_keyword]
            citations = self.extract_citations(content)
            registry.update(citations)

            logger.info(f"从 {path} 加载 {len(registry)} 个引用")

        except FileNotFoundError:
            logger.warning(f"引用注册表文件不存在: {path}")
        except Exception as e:
            logger.error(f"加载引用注册表失败: {e}")

        return registry

    def extract_citations(self, text: str) -> Set[str]:
        """
        提取文本中的引用标记

        支持格式:
        - [Author_2020]
        - [Author_2020_keyword]
        - [Author et al._2021]

        Args:
            text: 待提取的文本

        Returns:
            引用ID集合
        """
        # 匹配 [XXX_YYYY] 或 [XXX_YYYY_ZZZ] 格式
        # 允许作者名包含空格、点号等（如 "et al."）
        pattern = r'\[([A-Za-z][A-Za-z\s\.]+_\d{4}(?:_\w+)?)\]'

        matches = re.findall(pattern, text)

        # 清理空格
        citations = {m.strip() for m in matches}

        return citations

    def validate(self, original: str, modified: str) -> Dict:
        """
        验证引用完整性

        Args:
            original: 原始文本
            modified: 修改后文本

        Returns:
            {
                "original_citations": set,      # 原始引用集合
                "modified_citations": set,      # 修改后引用集合
                "missing": set,                 # 缺失的引用
                "added": set,                   # 新增的引用
                "integrity": float,             # 完整性分数 (0-1)
                "passed": bool                  # 是否通过（完整性=1.0）
            }
        """
        orig_cites = self.extract_citations(original)
        mod_cites = self.extract_citations(modified)

        missing = orig_cites - mod_cites
        added = mod_cites - orig_cites

        # 计算完整性：修改后保留了多少原始引用
        if not orig_cites:
            # 原始文本无引用，完整性视为100%
            integrity = 1.0
        else:
            # 完整性 = 保留的引用数 / 原始引用数
            retained = len(orig_cites & mod_cites)
            integrity = retained / len(orig_cites)

        passed = integrity == 1.0

        if not passed:
            logger.warning(
                f"引用完整性未达标: {integrity:.1%} "
                f"(缺失 {len(missing)} 个引用)"
            )

        return {
            "original_citations": orig_cites,
            "modified_citations": mod_cites,
            "missing": missing,
            "added": added,
            "integrity": integrity,
            "passed": passed
        }

    def validate_batch(
        self,
        pairs: List[Tuple[str, str]]
    ) -> List[Dict]:
        """
        批量验证引用完整性

        Args:
            pairs: (original, modified) 文本对列表

        Returns:
            验证结果列表
        """
        results = []

        for i, (original, modified) in enumerate(pairs):
            result = self.validate(original, modified)
            result["pair_index"] = i
            results.append(result)

        # 统计
        total = len(results)
        passed = sum(1 for r in results if r["passed"])
        avg_integrity = sum(r["integrity"] for r in results) / total if total > 0 else 0

        logger.info(
            f"批量验证完成: {passed}/{total} 通过, "
            f"平均完整性: {avg_integrity:.1%}"
        )

        return results

    def validate_against_registry(self, text: str) -> Dict:
        """
        验证文本中的引用是否都在注册表中

        Args:
            text: 待验证文本

        Returns:
            {
                "citations": set,           # 文本中的引用
                "valid": set,               # 在注册表中的引用
                "invalid": set,             # 不在注册表中的引用
                "coverage": float,          # 覆盖率 (0-1)
                "passed": bool              # 是否全部有效
            }
        """
        if not self.registry:
            logger.warning("未加载引用注册表，跳过注册表验证")
            return {
                "citations": set(),
                "valid": set(),
                "invalid": set(),
                "coverage": 0.0,
                "passed": False,
                "message": "No registry loaded"
            }

        citations = self.extract_citations(text)

        valid = citations & self.registry
        invalid = citations - self.registry

        coverage = len(valid) / len(citations) if citations else 1.0
        passed = len(invalid) == 0

        if not passed:
            logger.warning(
                f"发现 {len(invalid)} 个未注册的引用: {invalid}"
            )

        return {
            "citations": citations,
            "valid": valid,
            "invalid": invalid,
            "coverage": coverage,
            "passed": passed
        }

    def get_citation_statistics(self, text: str) -> Dict:
        """
        获取文本引用统计信息

        Args:
            text: 待分析文本

        Returns:
            {
                "total_citations": int,     # 总引用数
                "unique_citations": int,    # 唯一引用数
                "citation_list": list,      # 引用列表（按出现顺序）
                "citation_counts": dict     # 每个引用的出现次数
            }
        """
        # 提取所有引用（保留顺序）
        pattern = r'\[([A-Za-z][A-Za-z\s\.]+_\d{4}(?:_\w+)?)\]'
        all_citations = re.findall(pattern, text)

        # 统计次数
        citation_counts = {}
        for cite in all_citations:
            cite = cite.strip()
            citation_counts[cite] = citation_counts.get(cite, 0) + 1

        return {
            "total_citations": len(all_citations),
            "unique_citations": len(set(all_citations)),
            "citation_list": [c.strip() for c in all_citations],
            "citation_counts": citation_counts
        }
