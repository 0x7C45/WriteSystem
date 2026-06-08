---
skill: anti-aigc
phase: 3.5
trigger: conditional
dependencies:
  - assess_aigc_risk
  - Phase 3 completion
purpose: 降低AI生成内容检测风险的全流程对抗处理
version: 1.0.0
---

# Anti-AIGC Skill

> 职责: 论文AI反检测全流程 — 从检测基线到迭代优化
> 触发条件: Phase 3 终审中 `assess_aigc_risk` 返回高风险，或用户显式要求

---

## 一、Skill 定位

### 1.1 在管线中的位置

```
Phase 3 (排版终审) → assess_aigc_risk 高风险 → Phase 3.5 (降AI) → 返回 Phase 3 Step 3.4
```

### 1.2 核心目标

- **主目标**: 将AI生成内容的检测风险降至安全阈值以下
- **约束条件**: 
  - 保持语义完整性（改写后意思不变）
  - 保持学术规范性（逻辑严密、引用准确）
  - 保持格式一致性（与格式规范匹配）

### 1.3 质量底线

| 指标 | 底线要求 |
|------|---------|
| AIGC检测分 | 所有段落 < 阈值（GPTZero < 0.7, Originality < 0.6） |
| 语义保真度 | 改写前后相似度 > 0.85 |
| 学术规范 | 引用完整性 100%，逻辑连贯性人工评审通过 |
| 最大迭代次数 | 3轮（超出后人工介入） |

---

## 二、输入与输出

### 2.1 输入

| 来源 | 文件/数据 |
|------|----------|
| Phase 3 产物 | `06_最终交付/正文草稿_含参考文献.md` |
| 格式规范 | `00_订单信息/格式规范.md` |
| 引用注册表 | `05_撰写过程/_引用编号注册表.md` |
| 文献索引卡 | `04_参考文献/literature_cards/*.md` |
| 风险评估 | `assess_aigc_risk` 的检测报告 |

### 2.2 输出

| 文件 | 内容 |
|------|------|
| `06_最终交付/{论文标题}_终稿.docx` | 降AI后的终稿（替换原版） |
| `06_最终交付/降AI处理报告.md` | 完整处理过程记录 |
| `06_最终交付/降AI前后对比.md` | 典型段落改写前后对比 |
| `06_最终交付/AIGC检测分数变化.json` | 各检测器的分数变化轨迹 |

---

## 三、执行流程（5 个 Phase）

### Phase 1: 检测基线

**目标**: 建立多维度的AI检测基线，定位高危段落

#### Step 1.1 并行检测

并行调用以下检测器：

```python
detectors = [
    "gptzero",           # 英文内容主力
    "originality_ai",    # 英文+多语言
    "cnki_aigc",         # 中文学术专用（如可用）
    "zerogpt",           # 备用英文检测器
]
```

每个检测器返回：
- 全文总分（0-1，越高越像AI）
- 逐段落分数
- 高危句子标记

#### Step 1.2 生成热力图

```
输出格式：06_最终交付/AIGC热力图.md

# AIGC 检测热力图

## 第1章 绪论
### 1.1 研究背景
- 段落1: GPTZero=0.82 ⚠️ | Originality=0.71 ⚠️ | 知网=0.65
- 段落2: GPTZero=0.45 ✓ | Originality=0.38 ✓ | 知网=0.42 ✓

[标记: ⚠️ 高危 (>阈值), ✓ 安全, ⚡ 极高危 (>0.85)]
```

#### Step 1.3 定位高危段落

- 提取所有 **至少一个检测器标记为高危** 的段落
- 按章节归类
- 生成待处理列表：`06_最终交付/高危段落清单.json`

```json
{
  "high_risk_paragraphs": [
    {
      "chapter": "第1章",
      "section": "1.1",
      "paragraph_id": "1.1.1",
      "original_text": "...",
      "scores": {
        "gptzero": 0.82,
        "originality": 0.71
      },
      "reason": "句式过于规整，词汇重复度高"
    }
  ]
}
```

#### Gate 1.1 基线完整性检查

- 所有段落都有至少2个检测器的分数？
- 高危段落清单不为空（否则跳过后续处理）？

---

### Phase 2: 生成层对抗（可选）

**触发条件**: 高危段落占比 > 30%，或用户配置 `regenerate_mode=true`

**目标**: 用对抗性提示词重新生成高危段落

#### Step 2.1 对抗性重生成

对每个高危段落执行：

```python
prompt_template = f"""
你是一位资深学术写作专家。请将以下AI生成的段落改写为**真人撰写风格**：

原始段落：
{paragraph}

改写要求：
1. 保持核心观点和逻辑链不变
2. 增加句式多样性（长短句交错、主被动混合）
3. 使用更自然的学术表达（避免模板化句式）
4. 保留所有引用标记 [cite_key]
5. 字数误差 ±10%

输出格式：仅返回改写后的段落，不加任何说明。
"""

# 解码参数对抗配置
generation_config = {
    "temperature": 0.9,      # 提高随机性
    "top_p": 0.95,           # 扩大采样范围
    "frequency_penalty": 0.5, # 降低词汇重复
    "presence_penalty": 0.3   # 鼓励新词
}
```

#### Step 2.2 重生成质量检查

对每个重生成段落：
- 语义相似度 > 0.85？（用 sentence-transformers 计算）
- 引用标记完整性 100%？
- 字数在 ±10% 范围内？

不通过 → 标记为"重生成失败" → 进入 Phase 3 后处理

#### Gate 2.1 重生成有效性

- 重生成成功率 > 70%？
- 失败段落已标记？

---

### Phase 3: 后处理层对抗

**目标**: 通过规则驱动的后处理降低AI特征

#### 阶段1: 统计特征多样化

对每个段落执行：

```python
def diversify_statistics(paragraph):
    """
    调整统计分布使其接近人类写作
    """
    # 1. 词频分布平滑化
    word_freq = get_word_frequency(paragraph)
    if max(word_freq.values()) > 5:  # 高频词过多
        replace_high_freq_words(paragraph, threshold=5)
    
    # 2. 句长方差增加
    sentences = split_sentences(paragraph)
    sentence_lengths = [len(s) for s in sentences]
    if variance(sentence_lengths) < 50:  # 句长过于均匀
        merge_short_sentences()       # 合并短句
        split_long_sentences()        # 拆分长句
    
    # 3. 标点符号多样化
    if count_punctuation(paragraph)[','] > 0.7:  # 逗号占比过高
        replace_with_semicolon()      # 部分逗号改为分号
        replace_with_dash()           # 部分逗号改为破折号
    
    return modified_paragraph
```

#### 阶段2: 句式结构变异

```python
def vary_sentence_structure(paragraph):
    """
    增加句式多样性
    """
    sentences = parse_sentences(paragraph)
    
    for i, sent in enumerate(sentences):
        # 1. 主被动转换（保持学术语气）
        if is_passive(sent) and passive_ratio > 0.6:
            sent = convert_to_active(sent)
        
        # 2. 从句重组
        if has_multiple_clauses(sent):
            sent = reorder_clauses(sent)  # "因为A，所以B" → "B，因为A"
        
        # 3. 连接词替换
        sent = replace_conjunctions(sent, avoid_repetition=True)
        
        sentences[i] = sent
    
    return join_sentences(sentences)
```

#### 阶段3: 段落结构重组

```python
def restructure_paragraph(paragraph):
    """
    重组段落逻辑链
    """
    # 1. 提取论点和论据
    claim = extract_main_claim(paragraph)
    evidences = extract_evidences(paragraph)
    
    # 2. 随机化论证顺序（保持逻辑合理性）
    # AI典型: 总-分-总
    # 人类多样: 分-总，总-分，夹叙夹议
    if current_structure == "总分总":
        new_structure = random.choice(["分总", "总分", "夹叙夹议"])
    
    # 3. 过渡句重写
    transitions = extract_transitions(paragraph)
    for t in transitions:
        if is_template_phrase(t):  # "综上所述"、"由此可见"
            t_new = generate_natural_transition(context)
            paragraph = paragraph.replace(t, t_new)
    
    return paragraph
```

#### Gate 3.1 后处理质量检查

对每个处理后的段落：
- 语义保真度 > 0.85？
- 引用完整性 100%？
- 学术语气保持（content-reviewer 审查）？

---

### Phase 4: 迭代验证

**目标**: 反复检测直到通过或达到最大迭代次数

#### Step 4.1 重新检测

- 对所有处理后的段落重新执行 Phase 1 的检测流程
- 生成新的热力图和高危清单

#### Step 4.2 分数对比

```json
{
  "iteration": 2,
  "global_scores": {
    "before": {"gptzero": 0.78, "originality": 0.72},
    "after":  {"gptzero": 0.65, "originality": 0.58}
  },
  "still_high_risk": [
    {"paragraph_id": "3.2.4", "gptzero": 0.71}
  ]
}
```

#### Step 4.3 决策

```python
if all_paragraphs_safe():
    proceed_to_phase5()
elif iteration < MAX_ITERATIONS:
    # 对仍不通过的段落进行二次处理
    for para in still_high_risk:
        # 策略升级：更激进的改写
        apply_aggressive_rewrite(para)
    iteration += 1
    goto_step_4_1()
else:
    # 达到最大迭代次数仍未通过
    flag_for_manual_review()
    generate_failure_report()
```

#### Gate 4.1 迭代终止条件

- 所有段落通过？→ 进入 Phase 5
- 达到最大迭代次数？→ 人工介入决策
- 分数持续不下降？→ 标记为"技术瓶颈"，建议人工重写

---

### Phase 5: 输出与验证

**目标**: 生成最终产物并进行全局验证

#### Step 5.1 语义保真度全局验证

```python
def validate_semantic_fidelity(original_md, modified_md):
    """
    验证改写后整体意思未偏离
    """
    # 1. 段落级相似度检查
    original_paras = split_paragraphs(original_md)
    modified_paras = split_paragraphs(modified_md)
    
    similarities = []
    for orig, mod in zip(original_paras, modified_paras):
        sim = cosine_similarity(embed(orig), embed(mod))
        similarities.append(sim)
        
        if sim < 0.85:
            flag_paragraph(orig, mod, sim)
    
    # 2. 关键论点完整性
    original_claims = extract_key_claims(original_md)
    modified_claims = extract_key_claims(modified_md)
    
    if not all_claims_preserved(original_claims, modified_claims):
        raise SemanticDriftError("核心论点丢失")
    
    return {
        "avg_similarity": mean(similarities),
        "min_similarity": min(similarities),
        "claims_preserved": True
    }
```

#### Step 5.2 生成降AI分析报告

```markdown
# 降AI处理报告

## 处理概要
- 开始时间: 2026-06-06 14:30:00
- 结束时间: 2026-06-06 15:12:00
- 迭代轮次: 2
- 处理段落数: 47

## 检测分数变化

| 检测器 | 处理前 | 处理后 | 降幅 |
|--------|--------|--------|------|
| GPTZero | 0.78 | 0.62 | -20.5% |
| Originality.ai | 0.72 | 0.55 | -23.6% |
| 知网AIGC | 0.69 | 0.58 | -15.9% |

## 高危段落处理详情

### 第1章 1.1节 段落3
- **原始分数**: GPTZero=0.82, Originality=0.71
- **处理方法**: 后处理层对抗（句式变异 + 段落重组）
- **处理后分数**: GPTZero=0.64, Originality=0.59
- **语义相似度**: 0.91

[典型改写示例见 降AI前后对比.md]

## 语义保真度验证
- 平均相似度: 0.89
- 最低相似度: 0.86（第3章 3.2.4段）
- 核心论点完整性: ✓ 通过
- 引用完整性: ✓ 100%

## 人工复核建议
以下段落虽已通过阈值，但建议人工复核：
- 第3章 3.2.4段（相似度=0.86，接近底线）
- 第5章 5.1.2段（迭代2轮仍需要激进改写）
```

#### Step 5.3 生成前后对比文档

选择典型高危段落（3-5个），生成对比：

```markdown
# 降AI前后对比

## 案例1: 第1章 1.1节 段落3

### 处理前（GPTZero=0.82）
> 研究背景表明，人工智能技术在教育领域的应用日益广泛。近年来，随着深度学习算法的不断发展，智能教育系统已经能够实现个性化学习推荐、自动批改作业等功能。这些技术的应用不仅提高了教学效率，还为学生提供了更加灵活的学习方式。然而，现有研究主要集中在技术实现层面，对于教育效果的长期影响缺乏系统性评估。

### 处理后（GPTZero=0.64）
> 人工智能技术正深刻改变着教育实践的面貌。以深度学习为代表的算法突破，使得智能教育系统具备了前所未有的能力——从学习路径的定制化推荐，到作业的自动化评阅，这些创新极大提升了教学效率，并为学习者创造了更为灵活的知识获取途径[cite_1]。不过，既往文献多聚焦于技术架构与实现细节，而对这些干预措施的长期教育成效，尚缺乏纵向追踪与系统性验证[cite_2][cite_3]。

### 改写策略
- 句式变异：拆分长句（"近年来...学习方式"拆为2句）
- 词汇替换：避免高频词重复（"应用"→"实践"/"干预"）
- 结构重组：论据前置（先讲能力，再讲技术）
- 过渡自然化："然而"→"不过"，"主要集中在"→"多聚焦于"
```

#### Step 5.4 替换终稿文件

```python
# 1. 将改写后的 Markdown 重新排版
run_format_pipeline(
    source="06_最终交付/正文草稿_含参考文献_降AI.md",
    template="01_格式模板/模板.docx",
    output="06_最终交付/{论文标题}_终稿.docx"
)

# 2. 备份原版（以防需要回滚）
shutil.copy(
    "06_最终交付/{论文标题}_终稿.docx",
    "06_最终交付/{论文标题}_终稿_降AI前备份.docx"
)

# 3. 生成完整性校验
validate_docx_integrity(output_docx)
```

#### Gate 5.1 最终验证

并行执行：
- `validate_docx_styles` — 排版未损坏
- `validate_citations` — 引用完整性
- `validate_word_count` — 字数在允许范围内
- `assess_aigc_risk` — 最终检测分数 < 阈值

全部通过 → 返回 Phase 3 Step 3.4 继续终审流程

---

## 四、技术栈

### 4.1 检测器 API

| 检测器 | 用途 | API Endpoint |
|--------|------|--------------|
| GPTZero | 英文主力 | `https://api.gptzero.me/v2/predict` |
| Originality.ai | 多语言 | `https://api.originality.ai/scan` |
| 知网AIGC | 中文学术 | 需接入高校账号或API密钥 |
| ZeroGPT | 备用 | `https://zerogpt.com/api` |

### 4.2 NLP工具

```python
tools = {
    "sentence_embedding": "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
    "syntax_parser": "spaCy (zh_core_web_sm + en_core_web_sm)",
    "semantic_similarity": "cosine_similarity from sklearn",
    "text_diversity_metrics": "lexical_diversity, mtld"
}
```

### 4.3 后处理规则库

路径: `skills/anti-aigc/rules/`

```
rules/
├── statistical_transforms.py   # 统计特征变换规则
├── syntactic_variations.py     # 句法变异规则
├── paragraph_restructure.py    # 段落重组规则
├── academic_style_lexicon.json # 学术风格词汇表
└── template_phrase_blacklist.json # AI模板短语黑名单
```

---

## 五、配置选项

在 `00_订单信息/订单摘要.md` 的 frontmatter 中配置：

```yaml
anti_aigc:
  enabled: true                # 是否启用降AI（默认根据风险自动触发）
  detection_threshold:          # 检测阈值
    gptzero: 0.70
    originality: 0.60
    cnki: 0.65
  regenerate_mode: false        # 是否启用生成层对抗（默认仅后处理）
  max_iterations: 3             # 最大迭代次数
  semantic_fidelity_min: 0.85   # 语义保真度底线
  aggressive_rewrite: false     # 是否允许激进改写（可能降低可读性）
```

---

## 六、故障处理

### 6.1 常见失败场景

| 场景 | 原因 | 应对策略 |
|------|------|---------|
| 分数持续不下降 | 段落本身AI特征过强 | 建议人工重写 + 提供改写模板 |
| 语义保真度不达标 | 改写过度 | 回滚到上一轮 + 降低改写强度 |
| 引用丢失 | 正则替换错误 | 从引用注册表恢复 + 锁定引用标记 |
| 检测器API超时 | 网络或配额问题 | 降级到备用检测器 |

### 6.2 人工介入决策树

```
达到最大迭代次数 → 生成失败报告 → 提交 paper-advisor
  ├─ advisor=REVISE → 标记需人工重写的段落 → 用户修改后重新执行
  ├─ advisor=DISCUSS → 暂停，等待用户决策
  └─ advisor=PASS_WITH_RISK → 记录风险点 → 继续交付
```

---

## 七、质量保证

### 7.1 自动化测试

在 `skills/anti-aigc/tests/` 中提供：

```python
test_cases = [
    {
        "name": "高频词处理",
        "input": "研究表明研究方法研究结果研究意义...",
        "expected_diversity": "词频最大值 ≤ 3"
    },
    {
        "name": "引用完整性",
        "input": "...根据文献[Zhang_2020]的研究...",
        "expected": "处理后引用标记 [Zhang_2020] 仍存在"
    },
    {
        "name": "语义保真度",
        "input": "深度学习在图像识别中表现优异",
        "min_similarity": 0.85
    }
]
```

### 7.2 人工抽检

每次降AI处理后，随机抽取 10% 段落进行人工评审：
- 可读性（5分制）
- 学术规范性（5分制）
- 意思保真度（5分制）

评分 < 4.0 → 标记为"需优化" → 纳入规则库改进

---

## 八、与管线其他部分的交互

### 8.1 输入依赖

| 依赖 | 来源 | 用途 |
|------|------|------|
| 正文草稿 | Phase 2 | 待处理的原始内容 |
| 引用注册表 | Phase 2 | 验证引用完整性 |
| 格式规范 | Phase 0 | 重新排版时使用 |
| 风险评估 | Phase 3 | 触发条件判断 |

### 8.2 输出反馈

| 反馈 | 目标 | 内容 |
|------|------|------|
| 降AI后终稿 | Phase 3 | 替换原 docx |
| 处理报告 | Phase 3 | 供 paper-advisor M4 审查 |
| 失败标记 | Phase 3 | 人工介入决策 |

---

## 九、使用示例

### 9.1 自动触发（推荐）

```bash
# Phase 3 执行时自动检测并触发
# 无需手动调用
```

### 9.2 手动触发

```bash
# 在项目根目录执行
python -m skills.anti_aigc \
  --input "06_最终交付/正文草稿_含参考文献.md" \
  --config "00_订单信息/订单摘要.md" \
  --output "06_最终交付"
```

### 9.3 仅检测不处理（Dry Run）

```bash
python -m skills.anti_aigc \
  --input "06_最终交付/正文草稿_含参考文献.md" \
  --dry-run \
  --output "06_最终交付/AIGC检测报告.md"
```

---

## 十、版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-06-06 | 初始版本，实现5阶段完整流程 |

---

## 附录：关键算法伪代码

### A1. 主控流程

```python
def anti_aigc_pipeline(input_md, config):
    # Phase 1: 检测基线
    baseline = parallel_detect(input_md, detectors=config.detectors)
    high_risk_paras = filter_high_risk(baseline, threshold=config.threshold)
    
    if not high_risk_paras:
        return {"status": "safe", "report": generate_report(baseline)}
    
    # Phase 2: 生成层对抗（可选）
    if config.regenerate_mode:
        regenerated = regenerate_paragraphs(high_risk_paras, config)
        high_risk_paras = update_with_regenerated(high_risk_paras, regenerated)
    
    # Phase 3: 后处理层对抗
    for para in high_risk_paras:
        para_new = diversify_statistics(para)
        para_new = vary_sentence_structure(para_new)
        para_new = restructure_paragraph(para_new)
        
        # 语义验证
        if semantic_similarity(para, para_new) < config.semantic_fidelity_min:
            rollback(para)
            apply_conservative_rewrite(para)
    
    # Phase 4: 迭代验证
    for iteration in range(config.max_iterations):
        new_baseline = parallel_detect(input_md, detectors=config.detectors)
        still_high_risk = filter_high_risk(new_baseline, threshold=config.threshold)
        
        if not still_high_risk:
            break
        
        if iteration == config.max_iterations - 1:
            return {"status": "failed", "high_risk": still_high_risk}
        
        # 二次处理（更激进）
        for para in still_high_risk:
            apply_aggressive_rewrite(para)
    
    # Phase 5: 输出
    validate_semantic_fidelity(original_md, input_md)
    validate_citations(input_md)
    
    report = generate_full_report(baseline, new_baseline, iterations)
    return {"status": "success", "report": report, "output": input_md}
```

### A2. 句式变异核心算法

```python
def vary_sentence_structure(sentence):
    parsed = syntax_parse(sentence)
    
    # 1. 主被动转换
    if parsed.voice == "passive" and random() < 0.5:
        sentence = passive_to_active(parsed)
    
    # 2. 从句重组
    if len(parsed.clauses) > 1:
        clauses = parsed.clauses
        shuffle(clauses)  # 随机重排（保持逻辑合理性）
        sentence = join_clauses(clauses)
    
    # 3. 连接词替换
    conjunctions = extract_conjunctions(sentence)
    for conj in conjunctions:
        if conj in TEMPLATE_CONJUNCTIONS:
            replacement = sample_from_lexicon(conj, avoid_history=True)
            sentence = sentence.replace(conj, replacement)
    
    return sentence
```
