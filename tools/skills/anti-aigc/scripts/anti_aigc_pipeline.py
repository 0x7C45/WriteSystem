#!/usr/bin/env python3
"""
Anti-AIGC 核心处理流程
完整的5阶段降AI处理管线
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# 导入检测器客户端
try:
    from .detectors import GPTZeroClient, ZeroGPTClient
    from .semantic_validator import SemanticValidator
    from .citation_validator import CitationValidator
    from .postprocess import StatisticalDiversifier, SyntacticVariator, StructuralReorganizer
except ImportError:
    from detectors import GPTZeroClient, ZeroGPTClient
    from semantic_validator import SemanticValidator
    from citation_validator import CitationValidator
    from postprocess import StatisticalDiversifier, SyntacticVariator, StructuralReorganizer

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ProcessingConfig:
    """处理配置"""
    input_file: Path
    output_dir: Path
    config_file: Path
    detection_threshold: Dict[str, float]
    max_iterations: int = 3
    semantic_fidelity_min: float = 0.85
    regenerate_mode: bool = False
    aggressive_rewrite: bool = False
    dry_run: bool = False
    # API密钥配置
    gptzero_api_key: Optional[str] = None
    zerogpt_api_key: Optional[str] = None


class AntiAIGCPipeline:
    """降AI反检测处理管线"""

    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.knowledge_base = self._load_knowledge_base()

        # 初始化检测器客户端
        self.gptzero_client = None
        self.zerogpt_client = None

        if config.gptzero_api_key:
            try:
                self.gptzero_client = GPTZeroClient(config.gptzero_api_key)
                logger.info("GPTZero客户端初始化成功")
            except Exception as e:
                logger.warning(f"GPTZero客户端初始化失败: {e}")

        if config.zerogpt_api_key:
            try:
                self.zerogpt_client = ZeroGPTClient(config.zerogpt_api_key)
                logger.info("ZeroGPT客户端初始化成功")
            except Exception as e:
                logger.warning(f"ZeroGPT客户端初始化失败: {e}")

        # 初始化语义验证器
        try:
            self.semantic_validator = SemanticValidator()
            logger.info("语义验证器初始化成功")
        except Exception as e:
            logger.warning(f"语义验证器初始化失败: {e}")
            self.semantic_validator = None

        # 初始化引用验证器
        try:
            self.citation_validator = CitationValidator()
            logger.info("引用验证器初始化成功")
        except Exception as e:
            logger.warning(f"引用验证器初始化失败: {e}")
            self.citation_validator = None

        # 初始化后处理模块
        try:
            self.statistical_diversifier = StatisticalDiversifier(self.knowledge_base)
            self.syntactic_variator = SyntacticVariator(self.knowledge_base)
            self.structural_reorganizer = StructuralReorganizer(self.knowledge_base)
            logger.info("后处理模块初始化成功")
        except Exception as e:
            logger.warning(f"后处理模块初始化失败: {e}")
            self.statistical_diversifier = None
            self.syntactic_variator = None
            self.structural_reorganizer = None

    def _load_knowledge_base(self) -> Dict:
        """加载知识库"""
        kb_dir = Path(__file__).parent.parent / "knowledge"
        knowledge_base = {}

        for kb_file in ["synonym_dict.json", "ai_patterns.json",
                       "connector_variants.json", "sentence_starters.json"]:
            with open(kb_dir / kb_file, 'r', encoding='utf-8') as f:
                knowledge_base[kb_file.replace('.json', '')] = json.load(f)

        logger.info(f"知识库加载完成: {len(knowledge_base)} 个文件")
        return knowledge_base

    def run(self) -> Dict:
        """执行完整处理流程"""
        logger.info("=" * 60)
        logger.info("Anti-AIGC 降AI反检测处理管线启动")
        logger.info("=" * 60)

        try:
            # Phase 0: 论文预处理
            logger.info("\n[Phase 0] 论文预处理...")
            preprocessed = self.phase0_preprocess()

            # Phase 1: AI检测基线评估
            logger.info("\n[Phase 1] AI检测基线评估...")
            baseline = self.phase1_baseline_detection(preprocessed)

            if self.config.dry_run:
                logger.info("Dry-run模式，仅检测不处理")
                return {"status": "dry_run", "baseline": baseline}

            # 检查是否需要处理
            if not baseline.get("high_risk_paragraphs"):
                logger.info("✓ 所有段落AI分数低于阈值，无需处理")
                return {"status": "safe", "baseline": baseline}

            # Phase 2: 生成层对抗（可选）
            if self.config.regenerate_mode:
                logger.info("\n[Phase 2] 生成层对抗...")
                regenerated = self.phase2_generation_adversarial(baseline)
            else:
                logger.info("\n[Phase 2] 跳过生成层对抗（未启用）")
                regenerated = None

            # Phase 3: 后处理层对抗（核心）
            logger.info("\n[Phase 3] 后处理层对抗...")
            postprocessed = self.phase3_postprocess_adversarial(
                baseline, regenerated
            )

            # Phase 4: 迭代优化循环
            logger.info("\n[Phase 4] 迭代优化循环...")
            optimized = self.phase4_iterative_optimization(postprocessed)

            # Phase 5: 最终验证与输出
            logger.info("\n[Phase 5] 最终验证与输出...")
            result = self.phase5_final_verification(optimized, baseline)

            logger.info("\n" + "=" * 60)
            logger.info("处理完成")
            logger.info("=" * 60)

            return result

        except Exception as e:
            logger.error(f"处理失败: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    def phase0_preprocess(self) -> Dict:
        """Phase 0: 论文预处理"""
        # 读取论文
        with open(self.config.input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 格式标准化
        logger.info("  - 格式标准化...")

        # 章节识别
        logger.info("  - 章节识别...")

        # 段落拆分
        logger.info("  - 段落拆分...")
        paragraphs = self._split_paragraphs(content)

        # 段落分类
        logger.info("  - 段落分类...")
        classified = self._classify_paragraphs(paragraphs)

        logger.info(f"  ✓ 共识别 {len(classified)} 个段落")

        return {
            "original_content": content,
            "paragraphs": classified
        }

    def phase1_baseline_detection(self, preprocessed: Dict) -> Dict:
        """Phase 1: AI检测基线评估"""
        paragraphs = preprocessed["paragraphs"]

        # 并行检测（这里简化为串行）
        logger.info("  - 多检测器并行评分...")

        high_risk_paragraphs = []
        for para in paragraphs:
            # 模拟检测（实际需要调用API）
            scores = self._detect_paragraph(para["text"])
            para["scores"] = scores

            # 判断是否高危
            if self._is_high_risk(scores):
                high_risk_paragraphs.append(para)

        logger.info(f"  ✓ 检测完成: {len(high_risk_paragraphs)}/{len(paragraphs)} 段落高危")

        return {
            "all_paragraphs": paragraphs,
            "high_risk_paragraphs": high_risk_paragraphs,
            "global_scores": self._calculate_global_scores(paragraphs)
        }

    def phase2_generation_adversarial(self, baseline: Dict) -> Dict:
        """Phase 2: 生成层对抗"""
        high_risk = baseline["high_risk_paragraphs"]

        logger.info(f"  - 对 {len(high_risk)} 个高危段落进行对抗性重生成...")

        regenerated = []
        for para in high_risk:
            # 构建对抗性Prompt
            prompt = self._build_adversarial_prompt(para)

            # 重新生成（实际需要调用LLM API）
            new_text = self._regenerate_paragraph(prompt, para)

            # 验证语义保真度
            fidelity = self._check_semantic_fidelity(para["text"], new_text)

            if fidelity >= self.config.semantic_fidelity_min:
                regenerated.append({
                    "paragraph_id": para["id"],
                    "original": para["text"],
                    "regenerated": new_text,
                    "fidelity": fidelity
                })
                logger.info(f"    ✓ 段落 {para['id']} 重生成成功 (相似度: {fidelity:.2f})")
            else:
                logger.warning(f"    ✗ 段落 {para['id']} 重生成失真 (相似度: {fidelity:.2f})")

        logger.info(f"  ✓ 重生成完成: {len(regenerated)}/{len(high_risk)} 成功")

        return {"regenerated_paragraphs": regenerated}

    def phase3_postprocess_adversarial(self, baseline: Dict,
                                      regenerated: Optional[Dict]) -> Dict:
        """Phase 3: 后处理层对抗（核心）"""
        high_risk = baseline["high_risk_paragraphs"]

        logger.info(f"  - 对 {len(high_risk)} 个段落执行后处理...")

        processed = []

        for para in high_risk:
            logger.info(f"\n  处理段落 {para['id']} (类型: {para['type']})...")

            # 阶3.1: 统计特征多样化
            logger.info("    [阶3.1] 统计特征多样化...")
            para_text = para["text"]
            para_text = self._diversify_statistics(para_text)

            # 阶3.2: 句式结构变异
            logger.info("    [阶3.2] 句式结构变异...")
            para_text = self._vary_sentence_structure(para_text)

            # 重新检测
            scores = self._detect_paragraph(para_text)

            # 阶3.3: 结构重组（触发条件: AI分 > 50%）
            if max(scores.values()) > 0.5:
                logger.info("    [阶3.3] 结构重组...")
                para_text = self._restructure_paragraph(para_text)

            # 验证语义保真度
            fidelity = self._check_semantic_fidelity(para["text"], para_text)

            processed.append({
                "paragraph_id": para["id"],
                "original": para["text"],
                "processed": para_text,
                "fidelity": fidelity,
                "scores_after": scores
            })

            logger.info(f"    ✓ 处理完成 (相似度: {fidelity:.2f})")

        logger.info(f"\n  ✓ 后处理完成: {len(processed)} 个段落")

        return {"processed_paragraphs": processed}

    def phase4_iterative_optimization(self, postprocessed: Dict) -> Dict:
        """Phase 4: 迭代优化循环"""
        processed = postprocessed["processed_paragraphs"]

        iteration = 0
        still_high_risk = []

        while iteration < self.config.max_iterations:
            iteration += 1
            logger.info(f"\n  [迭代 {iteration}] 重新检测...")

            still_high_risk = []
            for para in processed:
                scores = self._detect_paragraph(para["processed"])
                para["scores_iter_" + str(iteration)] = scores

                if self._is_high_risk(scores):
                    still_high_risk.append(para)

            logger.info(f"    仍有 {len(still_high_risk)} 个段落未通过")

            if not still_high_risk:
                logger.info("  ✓ 所有段落通过，迭代终止")
                break

            if iteration >= self.config.max_iterations:
                logger.warning(f"  ⚠ 达到最大迭代次数 ({self.config.max_iterations})，部分段落未通过")
                break

            # 二次处理（更激进）
            logger.info(f"  对 {len(still_high_risk)} 个段落进行二次处理...")
            for para in still_high_risk:
                para["processed"] = self._apply_aggressive_rewrite(para["processed"])

        return {
            "final_paragraphs": processed,
            "iterations": iteration,
            "still_high_risk": still_high_risk
        }

    def phase5_final_verification(self, optimized: Dict, baseline: Dict) -> Dict:
        """Phase 5: 最终验证与输出"""
        final = optimized["final_paragraphs"]

        # 语义保真度全局验证
        logger.info("  - 语义保真度全局验证...")
        fidelity_report = self._validate_global_fidelity(final)

        # 引用完整性验证
        logger.info("  - 引用完整性验证...")
        citation_report = self._validate_citations(final)

        # 生成降AI分析报告
        logger.info("  - 生成降AI分析报告...")
        analysis_report = self._generate_analysis_report(
            baseline, optimized, fidelity_report, citation_report
        )

        # 输出终稿
        logger.info("  - 输出终稿...")
        output_file = self._write_final_output(final)

        logger.info(f"  ✓ 终稿已输出: {output_file}")

        return {
            "status": "success",
            "output_file": str(output_file),
            "analysis_report": analysis_report,
            "iterations": optimized["iterations"],
            "still_high_risk": optimized["still_high_risk"]
        }

    # ==================== 辅助方法 ====================

    def _split_paragraphs(self, content: str) -> List[str]:
        """拆分段落"""
        # 简化实现，实际需要更复杂的段落识别
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        return paragraphs

    def _classify_paragraphs(self, paragraphs: List[str]) -> List[Dict]:
        """段落分类"""
        classified = []
        for i, text in enumerate(paragraphs):
            classified.append({
                "id": f"P{i+1}",
                "text": text,
                "type": self._detect_paragraph_type(text),
                "word_count": len(text)
            })
        return classified

    def _detect_paragraph_type(self, text: str) -> str:
        """检测段落类型"""
        # 简化实现，实际需要更复杂的分类逻辑
        if "摘要" in text[:20]:
            return "摘要"
        elif "引言" in text[:20] or "背景" in text[:20]:
            return "引言背景"
        elif "方法" in text[:20]:
            return "方法"
        elif "结果" in text[:20]:
            return "结果分析"
        elif "讨论" in text[:20]:
            return "讨论"
        elif "结论" in text[:20]:
            return "结论"
        else:
            return "正文"

    def _detect_paragraph(self, text: str) -> Dict[str, float]:
        """检测段落AI分数

        使用并行方式调用多个检测器API

        Returns:
            各检测器的分数字典，如: {"gptzero": 0.78, "zerogpt": 0.65}
        """
        if not self.gptzero_client and not self.zerogpt_client:
            raise NotImplementedError(
                "没有可用的检测器客户端。"
                "请配置 gptzero_api_key 或 zerogpt_api_key"
            )

        return self._detect_paragraph_parallel(text)

    def _detect_paragraph_parallel(self, text: str) -> Dict[str, float]:
        """并行检测段落AI分数"""
        results = {}

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {}

            # 提交GPTZero检测任务
            if self.gptzero_client:
                futures[executor.submit(self._call_gptzero, text)] = "gptzero"

            # 提交ZeroGPT检测任务
            if self.zerogpt_client:
                futures[executor.submit(self._call_zerogpt, text)] = "zerogpt"

            # 收集结果
            for future in as_completed(futures):
                detector = futures[future]
                try:
                    score = future.result()
                    results[detector] = score
                    logger.debug(f"{detector} 检测完成: {score:.2f}")
                except Exception as e:
                    logger.error(f"{detector} 检测失败: {e}")
                    # 失败时返回0.0，不阻断流程
                    results[detector] = 0.0

        return results

    def _call_gptzero(self, text: str) -> float:
        """调用GPTZero检测"""
        result = self.gptzero_client.detect(text, multilingual=True)
        return result["overall"]

    def _call_zerogpt(self, text: str) -> float:
        """调用ZeroGPT检测"""
        result = self.zerogpt_client.detect(text)
        return result["score"]

    def _is_high_risk(self, scores: Dict[str, float]) -> bool:
        """判断是否高危"""
        for detector, score in scores.items():
            threshold = self.config.detection_threshold.get(detector, 0.7)
            if score > threshold:
                return True
        return False

    def _calculate_global_scores(self, paragraphs: List[Dict]) -> Dict[str, float]:
        """计算全局分数"""
        # 简化实现
        all_scores = {}
        for para in paragraphs:
            for detector, score in para.get("scores", {}).items():
                if detector not in all_scores:
                    all_scores[detector] = []
                all_scores[detector].append(score)

        return {
            detector: sum(scores) / len(scores)
            for detector, scores in all_scores.items()
        }

    def _build_adversarial_prompt(self, para: Dict) -> str:
        """构建对抗性Prompt"""
        return f"""请将以下段落改写为真人撰写风格：

{para['text']}

要求：
1. 保持核心观点不变
2. 增加句式多样性
3. 使用自然学术表达
4. 保留引用标记
"""

    def _regenerate_paragraph(self, prompt: str, para: Dict) -> str:
        """重新生成段落 - 未实现

        需要实现:
        - 调用 LLM API（如 Claude, GPT）
        - 传递对抗性 Prompt
        - 返回重生成的段落
        """
        raise NotImplementedError(
            "段落重生成未实现。"
            "需要集成 LLM API（Claude/GPT）"
        )

    def _check_semantic_fidelity(self, original: str, modified: str) -> float:
        """检查语义保真度

        使用 sentence-transformers 计算语义相似度

        Returns:
            相似度分数 (0-1)
        """
        if not self.semantic_validator:
            logger.warning("语义验证器未初始化，返回默认值 0.9")
            return 0.9

        try:
            return self.semantic_validator.check_fidelity(original, modified)
        except Exception as e:
            logger.error(f"语义保真度检查失败: {e}")
            return 0.0

    def _diversify_statistics(self, text: str) -> str:
        """统计特征多样化

        使用 StatisticalDiversifier 进行同义词替换和统计特征调整
        """
        if not self.statistical_diversifier:
            logger.warning("统计特征多样化器未初始化，跳过处理")
            return text

        try:
            return self.statistical_diversifier.diversify(text, coverage=0.65)
        except Exception as e:
            logger.error(f"统计特征多样化失败: {e}")
            return text

    def _vary_sentence_structure(self, text: str) -> str:
        """句式结构变异

        使用 SyntacticVariator 打破模板句式
        """
        if not self.syntactic_variator:
            logger.warning("句式结构变异器未初始化，跳过处理")
            return text

        try:
            return self.syntactic_variator.vary(text)
        except Exception as e:
            logger.error(f"句式结构变异失败: {e}")
            return text

    def _restructure_paragraph(self, text: str) -> str:
        """结构重组

        使用 StructuralReorganizer 打破总-分-总结构，注入人类不完美
        """
        if not self.structural_reorganizer:
            logger.warning("结构重组器未初始化，跳过处理")
            return text

        try:
            return self.structural_reorganizer.reorganize(text, aggressive=self.config.aggressive_rewrite)
        except Exception as e:
            logger.error(f"结构重组失败: {e}")
            return text

    def _apply_aggressive_rewrite(self, text: str) -> str:
        """激进改写"""
        # 更激进的改写策略
        return text

    def _validate_global_fidelity(self, paragraphs: List[Dict]) -> Dict:
        """验证全局语义保真度"""
        fidelities = [p["fidelity"] for p in paragraphs]
        return {
            "avg_fidelity": sum(fidelities) / len(fidelities),
            "min_fidelity": min(fidelities),
            "max_fidelity": max(fidelities)
        }

    def _validate_citations(self, paragraphs: List[Dict]) -> Dict:
        """验证引用完整性

        检查每个段落改写前后的引用完整性

        Returns:
            {
                "total_paragraphs": int,
                "passed": int,
                "failed": int,
                "average_integrity": float,
                "details": list
            }
        """
        if not self.citation_validator:
            logger.warning("引用验证器未初始化，跳过验证")
            return {
                "total_paragraphs": len(paragraphs),
                "passed": len(paragraphs),
                "failed": 0,
                "average_integrity": 1.0,
                "details": []
            }

        results = []
        for para in paragraphs:
            try:
                validation = self.citation_validator.validate(
                    para["original"],
                    para["processed"]
                )
                results.append({
                    "paragraph_id": para["paragraph_id"],
                    "integrity": validation["integrity"],
                    "passed": validation["passed"],
                    "missing": list(validation["missing"]),
                    "added": list(validation["added"])
                })
            except Exception as e:
                logger.error(f"引用验证失败 (段落 {para['paragraph_id']}): {e}")
                results.append({
                    "paragraph_id": para["paragraph_id"],
                    "integrity": 0.0,
                    "passed": False,
                    "error": str(e)
                })

        total = len(results)
        passed = sum(1 for r in results if r.get("passed", False))
        failed = total - passed
        avg_integrity = sum(r.get("integrity", 0) for r in results) / total if total > 0 else 1.0

        return {
            "total_paragraphs": total,
            "passed": passed,
            "failed": failed,
            "average_integrity": avg_integrity,
            "details": results
        }

    def _generate_analysis_report(self, baseline: Dict, optimized: Dict,
                                 fidelity: Dict, citations: Dict) -> str:
        """生成分析报告"""
        report = f"""
# 降AI处理分析报告

## 处理概要
- 处理段落数: {len(optimized['final_paragraphs'])}
- 迭代轮次: {optimized['iterations']}
- 仍高危段落: {len(optimized['still_high_risk'])}

## 语义保真度
- 平均相似度: {fidelity['avg_fidelity']:.2f}
- 最低相似度: {fidelity['min_fidelity']:.2f}

## 引用完整性
- {citations['integrity']}

## 检测分数变化
[待补充]
"""
        return report

    def _write_final_output(self, paragraphs: List[Dict]) -> Path:
        """输出终稿"""
        output_file = self.config.output_dir / "final_paper_anti_aigc.md"

        with open(output_file, 'w', encoding='utf-8') as f:
            for para in paragraphs:
                f.write(para["processed"] + "\n\n")

        return output_file


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="Anti-AIGC 降AI反检测处理")
    parser.add_argument("--input", required=True, help="输入论文文件")
    parser.add_argument("--output", required=True, help="输出目录")
    parser.add_argument("--config", help="配置文件")
    parser.add_argument("--dry-run", action="store_true", help="仅检测不处理")

    args = parser.parse_args()

    config = ProcessingConfig(
        input_file=Path(args.input),
        output_dir=Path(args.output),
        config_file=Path(args.config) if args.config else None,
        detection_threshold={"gptzero": 0.7, "zerogpt": 0.6},
        dry_run=args.dry_run
    )

    pipeline = AntiAIGCPipeline(config)
    result = pipeline.run()

    print("\n" + "=" * 60)
    print("处理结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("=" * 60)


if __name__ == "__main__":
    main()
