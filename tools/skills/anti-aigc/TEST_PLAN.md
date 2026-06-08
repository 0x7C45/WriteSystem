# Anti-AIGC 端到端测试套件

## 测试目标

验证完整的降AI处理管线（Phase 0-5）在真实论文上的表现。

## 测试指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| AI分降幅 | > 20% | 处理后AI检测分数相比原始文本的降低幅度 |
| 语义保真度 | > 0.85 | 处理前后文本的语义相似度 |
| 引用完整性 | 100% | 引用标记必须完全保留 |
| 处理时间 | < 10分钟/5000字 | 完整处理的时间效率 |
| 迭代收敛率 | > 90% | 3轮内达标的段落比例 |

## 测试用例

### 测试论文准备

准备3-5篇不同学科的测试论文（约3000-5000字）：

1. **计算机科学** - 机器学习/深度学习主题
2. **教育学** - 教学方法/教育技术主题  
3. **经济学** - 实证研究/政策分析主题
4. **医学** (可选) - 临床研究/公共卫生主题
5. **社会学** (可选) - 社会现象/调查研究主题

**测试论文存放位置**：
```
tools/skills/anti-aigc/test_data/
├── papers/
│   ├── cs_machine_learning.md
│   ├── edu_personalized_learning.md
│   ├── econ_policy_analysis.md
│   ├── med_clinical_trial.md (可选)
│   └── soc_survey_research.md (可选)
└── results/
    ├── cs/
    ├── edu/
    └── econ/
```

## 测试流程

### 1. 仅检测模式（Dry-run）

验证检测器API是否正常工作，了解原始AI分数基线。

```bash
# 计算机科学论文
python scripts/anti_aigc_pipeline.py \
  --input test_data/papers/cs_machine_learning.md \
  --output test_data/results/cs \
  --dry-run

# 教育学论文
python scripts/anti_aigc_pipeline.py \
  --input test_data/papers/edu_personalized_learning.md \
  --output test_data/results/edu \
  --dry-run

# 经济学论文
python scripts/anti_aigc_pipeline.py \
  --input test_data/papers/econ_policy_analysis.md \
  --output test_data/results/econ \
  --dry-run
```

**预期输出**：
- 每个段落的AI检测分数
- 高危段落清单
- 全文平均AI分数

### 2. 完整处理模式

执行完整的Phase 0-5流程，生成降AI后的论文。

```bash
# 配置文件示例 (test_config.json)
{
  "gptzero_api_key": "YOUR_API_KEY",
  "zerogpt_api_key": "YOUR_API_KEY",
  "detection_threshold": {
    "gptzero": 0.7,
    "zerogpt": 0.6
  },
  "max_iterations": 3,
  "semantic_fidelity_min": 0.85,
  "regenerate_mode": false,
  "aggressive_rewrite": false
}

# 运行完整处理
python scripts/anti_aigc_pipeline.py \
  --input test_data/papers/cs_machine_learning.md \
  --output test_data/results/cs \
  --config test_config.json
```

**预期输出**：
- `final_paper_anti_aigc.md` - 降AI后的论文
- `analysis_report.md` - 处理分析报告
- `processing_log.txt` - 详细处理日志

### 3. 质量验证

对比处理前后的论文，验证质量指标。

```python
# 验证脚本 (scripts/verify_results.py)
import json
from pathlib import Path
from semantic_validator import SemanticValidator
from citation_validator import CitationValidator

def verify_results(original_file, processed_file, analysis_report):
    """验证处理结果"""
    
    # 1. AI分降幅
    with open(analysis_report) as f:
        report = json.load(f)
    
    baseline_score = report["baseline"]["global_scores"]["gptzero"]
    final_score = report["final"]["global_scores"]["gptzero"]
    reduction = (baseline_score - final_score) / baseline_score * 100
    
    print(f"AI分降幅: {reduction:.1f}% (目标 > 20%)")
    assert reduction > 20, "AI分降幅未达标"
    
    # 2. 语义保真度
    validator = SemanticValidator()
    with open(original_file) as f:
        original = f.read()
    with open(processed_file) as f:
        processed = f.read()
    
    fidelity = validator.check_fidelity(original, processed)
    print(f"语义保真度: {fidelity:.3f} (目标 > 0.85)")
    assert fidelity > 0.85, "语义保真度未达标"
    
    # 3. 引用完整性
    citation_val = CitationValidator()
    result = citation_val.validate(original, processed)
    
    print(f"引用完整性: {result['integrity']:.0%} (目标 100%)")
    assert result["integrity"] == 1.0, f"引用缺失: {result['missing']}"
    
    # 4. 处理时间
    processing_time = report["processing_time_seconds"]
    word_count = len(original)
    time_per_5k = processing_time / (word_count / 5000)
    
    print(f"处理时间: {time_per_5k:.1f}分钟/5000字 (目标 < 10分钟)")
    assert time_per_5k < 600, "处理时间过长"
    
    print("\n✅ 所有指标通过")
    return True

# 运行验证
verify_results(
    "test_data/papers/cs_machine_learning.md",
    "test_data/results/cs/final_paper_anti_aigc.md",
    "test_data/results/cs/analysis_report.json"
)
```

## 测试结果模板

### 测试报告格式

```markdown
# Anti-AIGC 测试报告

## 测试概要
- 测试日期: YYYY-MM-DD
- 测试论文数: X篇
- 通过率: X/X (XX%)

## 详细结果

### 论文1: 计算机科学 - 机器学习主题

| 指标 | 目标值 | 实际值 | 状态 |
|------|--------|--------|------|
| AI分降幅 | > 20% | 28.3% | ✅ 通过 |
| 语义保真度 | > 0.85 | 0.89 | ✅ 通过 |
| 引用完整性 | 100% | 100% | ✅ 通过 |
| 处理时间 | < 10分钟 | 8.5分钟 | ✅ 通过 |
| 迭代收敛率 | > 90% | 95% | ✅ 通过 |

**处理详情**:
- 原文字数: 4,523字
- 高危段落: 12/23 (52%)
- 迭代轮次: 2轮
- 最终高危段落: 1/23 (4%)

**问题记录**:
无

---

### 论文2: 教育学 - 个性化学习主题

| 指标 | 目标值 | 实际值 | 状态 |
|------|--------|--------|------|
| AI分降幅 | > 20% | 18.7% | ❌ 未达标 |
| 语义保真度 | > 0.85 | 0.91 | ✅ 通过 |
| 引用完整性 | 100% | 98% | ❌ 未达标 |
| 处理时间 | < 10分钟 | 11.2分钟 | ❌ 未达标 |
| 迭代收敛率 | > 90% | 88% | ❌ 未达标 |

**处理详情**:
- 原文字数: 5,812字
- 高危段落: 18/28 (64%)
- 迭代轮次: 3轮（达到上限）
- 最终高危段落: 3/28 (11%)

**问题记录**:
1. AI分降幅略低于目标 - 可能需要更激进的改写策略
2. 引用缺失1个 - [Chen_2021] 在Phase 3.3处理时丢失
3. 处理时间超标 - 检测器API响应较慢
4. 3个段落3轮迭代后仍未达标 - 需要分析原因

---

### 论文3: 经济学 - 政策分析主题

...

## 总结

### 通过率统计
- 总体通过率: 2/3 (67%)
- AI分降幅: 2/3 通过
- 语义保真度: 3/3 通过
- 引用完整性: 2/3 通过
- 处理时间: 2/3 通过
- 迭代收敛率: 2/3 通过

### 已知问题
1. **引用完整性缺陷** - Phase 3.3结构重组时可能遗漏引用
2. **处理时间波动** - 检测器API响应时间不稳定
3. **部分段落难以收敛** - 需要分析高AI分段落的特征

### 改进建议
1. 在Phase 3.3前后增加引用验证检查点
2. 实现检测器API缓存机制减少重复调用
3. 对难收敛段落启用aggressive_rewrite模式
4. 优化后处理算法参数（同义词覆盖率、句式变异强度等）

## 下一步行动
1. 修复引用完整性缺陷（优先级：P0）
2. 实现API缓存（优先级：P1）
3. 扩大测试集到10篇论文（优先级：P2）
4. 进行长期稳定性测试（优先级：P2）
```

## 自动化测试

### 测试脚本

```bash
#!/bin/bash
# test_suite.sh - 自动化测试套件

echo "=========================================="
echo "Anti-AIGC 端到端测试套件"
echo "=========================================="

# 配置
TEST_PAPERS=(
    "cs_machine_learning"
    "edu_personalized_learning"
    "econ_policy_analysis"
)

CONFIG_FILE="test_config.json"
RESULTS_DIR="test_data/results"

# 清理旧结果
rm -rf $RESULTS_DIR/*

# 运行测试
for paper in "${TEST_PAPERS[@]}"; do
    echo ""
    echo "测试论文: $paper"
    echo "------------------------------------------"
    
    python scripts/anti_aigc_pipeline.py \
        --input "test_data/papers/${paper}.md" \
        --output "${RESULTS_DIR}/${paper}" \
        --config "$CONFIG_FILE"
    
    if [ $? -eq 0 ]; then
        echo "✅ 处理完成"
    else
        echo "❌ 处理失败"
    fi
done

# 汇总结果
echo ""
echo "=========================================="
echo "生成测试报告"
echo "=========================================="

python scripts/generate_test_report.py \
    --results-dir "$RESULTS_DIR" \
    --output "TEST_REPORT.md"

echo "测试报告已生成: TEST_REPORT.md"
```

## 持续集成

将测试集成到CI/CD流程：

```yaml
# .github/workflows/test-anti-aigc.yml
name: Anti-AIGC Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run test suite
      env:
        GPTZERO_API_KEY: ${{ secrets.GPTZERO_API_KEY }}
        ZEROGPT_API_KEY: ${{ secrets.ZEROGPT_API_KEY }}
      run: |
        bash tools/skills/anti-aigc/test_suite.sh
    
    - name: Upload test results
      uses: actions/upload-artifact@v2
      with:
        name: test-results
        path: tools/skills/anti-aigc/TEST_REPORT.md
```
