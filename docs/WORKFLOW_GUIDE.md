# 论文撰写完整工作流指南

> WriteSystem v1.0.0 | 从需求到交付的完整流程

---

## 概览

WriteSystem 提供完整的论文撰写自动化管线，从原始资料到最终 DOCX，经历 5 个 Phase 和 4 个里程碑审查。

```
Phase 0          Phase 1a/1b        Phase 2           Phase 3          Phase 3.5
订单提炼     →   文献+规划     →   逐章撰写     →   排版终审     →   降AI(条件)
  ↓                ↓                 ↓                 ↓                 ↓
 M1              M2                M3                M4             完成交付
方向确认        骨架确认          草稿审查          交付确认
```

**预计耗时**：3-8 小时（取决于论文字数和复杂度）

---

## 启动方式

### 方式 1: 一句话启动（推荐）

```bash
bash scripts/run.sh ~/Desktop/论文资料 --auto
```

适用场景：材料齐全，信任 AI 能力，时间紧迫

**详细文档** → [`ONE_COMMAND_WORKFLOW.md`](ONE_COMMAND_WORKFLOW.md)

### 方式 2: 手动逐步流程

```bash
bash scripts/scaffold.sh my-paper
# 投放资料到 00_订单信息/原始资料/
# 告诉 AI "执行 Phase 0"
```

适用场景：首次使用，需要逐步了解每个阶段

**详细文档** → [`QUICKSTART.md`](QUICKSTART.md)

---

## Phase 0 — 订单提炼

### 目标
从用户提供的原始资料中提取结构化的论文需求和格式规范

### 输入
- 用户投放到 `00_订单信息/原始资料/` 的所有文件（任意格式）
  - 格式模板 (.docx)
  - 需求文件 (.pdf, .txt, .md)
  - 数据文件 (.xlsx, .csv)
  - 图片 (.jpg, .png)
  - 参考范文 (.pdf, .docx)
  - 用户笔记 (.txt, .md)

### 执行 Agent
`paper-order-analyst`

### 步骤
1. **扫描原始资料** — 识别每个文件的类型
2. **自动分类** — 模板 → 01_格式模板/, 数据 → 02_工作素材/
3. **分析模板** — 使用 `analyze_docx_template` 提取样式规范
4. **提炼订单摘要** — 标题、类型、学科、字数、截止日期、引用格式
5. **提炼格式规范** — 页边距、字体、行距、引用格式

### 质量门控
- Gate 0.1: content-reviewer 审查订单摘要完整性
- Gate 0.2: content-reviewer 审查格式规范完整性

### 输出
- `00_订单信息/订单摘要.md` — 结构化论文需求
- `00_订单信息/格式规范.md` — 完整格式要求
- `00_订单信息/原始资料/README.md` — 分类清单
- `01_格式模板/*.docx` — 格式模板（如有）
- `03_计划与方案/论文撰写计划输入.md` — 供 Phase 1b 使用

### 预计耗时
2-5 分钟

### 用户确认节点
- `interaction_level: minimal` → 自动继续
- `interaction_level: coarse` → 停止，确认订单理解正确
- `interaction_level: fine` → 停止，确认订单理解正确

---

## Phase 1a — 文献检索

### 目标
检索中英文文献并为每篇生成结构化索引卡

### 输入
- `00_订单信息/订单摘要.md` — 提取关键词和学科领域

### 执行 Agent
`paper-literature-agent`

### 步骤
1. **确定检索策略** — 中英文关键词、检索源、时间范围
2. **执行检索** — 知网、Google Scholar、arXiv、Semantic Scholar
3. **去重和初筛** — 按标题/DOI去重，阅读摘要排除不相关
4. **获取全文** — PDF 优先，CAJ 备用
5. **生成索引卡** — 核心发现、研究方法、与本文关系

### 质量门控
- Gate 1a.1: content-reviewer 审查检索策略
- Gate 1a.2: content-reviewer 审查索引卡质量和数量（本科≥15，硕士≥30）

### 输出
- `04_参考文献/literature_cards/{作者}_{年份}.md` × N
- `04_参考文献/literature_cards/_索引卡汇总.md`

### 预计耗时
30-60 分钟

---

## Phase 1b — 研究规划（与 1a 并行）

### 目标
阅读索引卡、撰写开题报告、生成细化骨架大纲

### 输入
- Phase 1a 产出的索引卡
- `00_订单信息/订单摘要.md`

### 执行 Agent
`paper-researcher`

### 步骤
1. **文献综合分析** — 识别研究缺口、确定方法选择
2. **撰写开题报告** — 研究背景 → 研究问题 → 文献综述概要 → 研究方法 → 预期贡献
3. **生成骨架大纲** — 细化到每个段落的 20-30 字要点
4. **生成核心论点摘要** — 200字以内

### 质量门控
- Gate 1b.G1: content-reviewer 审查文献基础
- Gate 1b.G2: content-reviewer 审查学术严谨性
- Gate 1b.G3: content-reviewer + data-auditor 联合审查骨架逻辑
- Gate 1b.G4: content-reviewer 结构连贯性审查

### 里程碑
- **M1 (方向确认)** — Phase 1a 完成后，paper-advisor 审查选题可行性
- **M2 (骨架确认)** — Phase 1b 完成后，paper-advisor 审查研究问题和方法论

### 输出
- `03_计划与方案/开题报告.md`
- `03_计划与方案/骨架大纲.md` — 细化到段落级别
- `03_计划与方案/核心论点摘要.md`
- `03_计划与方案/导师确认态.md` — M1 + M2 判定记录

### 预计耗时
30-60 分钟

### 用户确认节点
- `interaction_level: minimal` → M1/M2 自动通过（或自动修复）
- `interaction_level: coarse` → M2 通过后停止，确认骨架大纲
- `interaction_level: fine` → M2 通过后停止，确认骨架大纲

---

## Phase 2 — 逐章撰写

### 目标
按骨架大纲逐段撰写，引用文献索引卡和数据事实

### 输入
- `03_计划与方案/骨架大纲.md` — 每个段落的要点
- `04_参考文献/literature_cards/` — 文献索引卡
- `02_工作素材/data_facts.md` — 实验数据摘要

### 执行 Agent
`paper-copilot`

### 步骤
1. **章节计划确认** — 列出本章需要的文献和数据
2. **逐段撰写** — 使用 `search_blocks` 检索索引卡，`query_data_facts` 查询数据
3. **标记引用** — 使用 `[cite_key]` 格式
4. **更新引用注册表** — 确保同一文献引用编号一致
5. **章节合并** — 所有章节完成后合并为正文草稿

### 质量门控
- Gate 2.1: content-reviewer 章节计划审查
- Gate 2.2: validate_word_count + validate_chapter_citations + content-reviewer + data-auditor（每章）
- Gate 2.3: 合并后全局检查（总字数、引用一致性、数据一致性）

### 里程碑
- **M3 (草稿审查)** — 全文完成后，paper-advisor 审查连贯性和学术规范

### 输出
- `05_撰写过程/第N章_{标题}.md` × N
- `05_撰写过程/正文草稿.md` — 合并后全文
- `05_撰写过程/_引用编号注册表.md`

### 预计耗时
2-6 小时（取决于字数）

### 用户确认节点
- `interaction_level: minimal` → M3 自动通过（或自动修复）
- `interaction_level: coarse` → M3 通过后停止，确认正文草稿
- `interaction_level: fine` → 每章完成后停止，M3 通过后停止

---

## Phase 3 — 排版终审

### 目标
校验 Markdown、生成参考文献、排版 DOCX、终审、AIGC 风险评估

### 输入
- `05_撰写过程/正文草稿.md`
- `00_订单信息/格式规范.md`
- `01_格式模板/*.docx`
- `04_参考文献/literature_cards/`

### 执行 Agent
`paper-formatter`

### 步骤
1. **Markdown 就绪性检查（并行）**
   - validate_markdown_structure
   - validate_assets
   - validate_word_count
   - validate_citations
2. **引用生成与排序**
   - build_reference_list（按引用格式）
   - validate_citation_order
   - 追加参考文献列表到正文
3. **排版管道**
   - apply_minimax_c2（首选）或 apply_pandoc_templated（备用）
   - 输出 DOCX
4. **DOCX 成品校验（并行）**
   - validate_docx_styles / sections / layout / fonts / references
5. **终审**
   - content-reviewer + data-auditor
   - assess_aigc_risk

### 质量门控
- Gate 3.2: DOCX 校验通过

### 里程碑
- **M4 (交付确认)** — paper-advisor 最终审查

### AIGC 触发
如果 assess_aigc_risk 返回高风险 → 自动触发 Phase 3.5

### 输出
- `06_最终交付/Markdown就绪性报告.md`
- `06_最终交付/正文草稿_含参考文献.md`
- `06_最终交付/{论文标题}_终稿.docx`
- `06_最终交付/终审报告.md`
- `06_最终交付/排版历程报告.md`

### 预计耗时
10-30 分钟

### 用户确认节点
- `interaction_level: minimal` → M4 通过后停止，交付确认
- `interaction_level: coarse` → M4 通过后停止，交付确认
- `interaction_level: fine` → M4 通过后停止，交付确认

---

## Phase 3.5 — 降AI处理（条件触发）

### 目标
降低 AIGC 检测分数，保持语义保真度

### 触发条件
- Phase 3 中 assess_aigc_risk 返回高风险
- 或用户显式要求

### 执行 Skill
`skills/anti-aigc/`

### 步骤
1. **检测基线** — 多检测器并行评分（GPTZero / Originality / 知网）
2. **标记高危段落** — 生成逐段 AI 热力图
3. **后处理对抗**
   - 统计特征多样化（词频分布、句长方差）
   - 句式结构变异（主动/被动转换、从句重组）
   - 段落结构重组（逻辑链重排、过渡句重写）
4. **迭代验证** — 重新执行 assess_aigc_risk，直到通过或达到 3 轮
5. **语义保真度验证** — 确保改写后原文意思不变

### 输出
- `06_最终交付/{论文标题}_终稿.docx` — 替换原版
- `06_最终交付/降AI处理报告.md` — 前后对比 + 检测分数变化

### 预计耗时
20-40 分钟

---

## 里程碑审查 (M1-M4)

### M1 — 方向确认
- **时机**：Phase 1a 完成后
- **审查方**：paper-advisor
- **审查内容**：选题可行性、文献基础、资源可用性
- **判定**：PASS / REVISE / DISCUSS

### M2 — 骨架确认
- **时机**：Phase 1b 完成后
- **审查方**：paper-advisor
- **审查内容**：研究问题、方法论、框架逻辑、复杂度
- **判定**：PASS / REVISE / DISCUSS

### M3 — 草稿审查
- **时机**：Phase 2 完成后
- **审查方**：paper-advisor
- **审查内容**：全文连贯性、学术规范、引用一致性
- **判定**：PASS / REVISE / DISCUSS

### M4 — 交付确认
- **时机**：Phase 3 (+3.5) 完成后
- **审查方**：paper-advisor
- **审查内容**：排版质量、AIGC风险、最终完整性
- **判定**：PASS / REVISE / DISCUSS

### REVISE 处理
- `revise_mode: auto` → AI 自动修复，最多 2 轮
- `revise_mode: manual` → 暂停管线，通知用户问题，等待决策

---

## 交互粒度配置

通过 `00_订单信息/订单摘要.md` 的 frontmatter 控制：

```yaml
pipeline:
  interaction_level: coarse     # coarse | fine | minimal
  revise_mode: auto             # auto | manual
  max_revise_rounds: 2
```

### interaction_level

| 值 | 确认节点 | 适用场景 |
|----|---------|---------|
| `minimal` | 2 个：订单确认 + 交付确认 | 用户完全托管，只看结果 |
| `coarse` | 4 个：订单 + 骨架 + 草稿 + 交付 | 用户信任管线，只需关键决策 |
| `fine` | coarse + 每章写完确认 | 用户想逐章把控质量 |

### revise_mode

| 值 | 行为 | 适用场景 |
|----|------|---------|
| `auto` | AI 自动修复并重新提交 | 用户信任 AI 能自行纠错 |
| `manual` | 暂停管线，通知用户问题 | 用户想自己把控修改方向 |

---

## 常见问题

### Q1: 如何跳过某个 Phase？
A: 告诉 AI："跳过 Phase X，继续下一个"

### Q2: 如何修改中途配置？
A: 编辑 `00_订单信息/订单摘要.md` 的 pipeline 段，下一个检查点立即生效

### Q3: 如何手动写某一章？
A: 告诉 AI："第 3 章我自己写，跳过它"，然后手动创建 `05_撰写过程/第3章_xxx.md`

### Q4: 里程碑审查不通过怎么办？
A: 
- `revise_mode: auto` → AI 自动回到对应步骤修改
- `revise_mode: manual` → 暂停，等待你修改或提供指导

### Q5: 如何查看当前进度？
A: 查看 `03_计划与方案/导师确认态.md` 了解各里程碑状态

---

## 参考文档

- **一句话启动** → [`ONE_COMMAND_WORKFLOW.md`](ONE_COMMAND_WORKFLOW.md)
- **手动流程** → [`QUICKSTART.md`](QUICKSTART.md)
- **完整管线规范** → [`../spec/conventions/pipeline-spec.md`](../spec/conventions/pipeline-spec.md)
- **配置说明** → [`../spec/conventions/pipeline-config.md`](../spec/conventions/pipeline-config.md)
- **Agent 定义** → [`../tools/agent/*.md`](../tools/agent/)
- **MCP 工具** → [`../tools/mcp-servers/paper-tools-mcp/MANIFEST.yml`](../tools/mcp-servers/paper-tools-mcp/MANIFEST.yml)
