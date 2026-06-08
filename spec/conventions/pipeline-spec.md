# 论文撰写管线完整规范

> 版本: v1.0.0 | 所属: WriteSystem spec/conventions
> 基于: 论文撰写工作流全景报告 (ArticleSystem/工作流架构/)

---

## 一、管线总览

```
Phase 0          Phase 1a/1b        Phase 2           Phase 3          Phase 3.5
订单提炼     →   文献+规划     →   逐章撰写     →   排版终审     →   降AI(条件)
(1 Agent)        (2 Agent并行)      (1 Agent)         (1 Agent)        (1 Skill)

  M1              M2                M3                M4
  方向确认         骨架确认           草稿审查           交付确认
  (advisor)       (advisor)         (advisor)         (advisor)
```

每个 Phase 有明确的**入口条件 → 执行步骤 → 门控检查 → 出口产物**。

---

## 二、全局约定

### 2.1 项目目录结构（每个项目独立）

```
projects/{project_name}/
...
```

### 2.2 管线配置

每次交互行为由 `00_订单信息/订单摘要.md` frontmatter 中的 `pipeline` 段控制。
详见 `spec/conventions/pipeline-config.md`。

```yaml
pipeline:
  interaction_level: coarse     # coarse | fine | minimal
  revise_mode: auto             # auto | manual
  max_revise_rounds: 2
```

### 2.3 里程碑与审查

| 里程碑 | 触发 | 审查方 | 审查内容 | 判定 |
|--------|------|--------|---------|------|
| M1 | Phase 0 + Phase 1a 完成 | paper-advisor | 选题可行性、文献基础 | PASS / REVISE / DISCUSS |
| M2 | Phase 1b 完成 | paper-advisor | 研究问题、方法论、框架逻辑 | PASS / REVISE / DISCUSS |
| M3 | Phase 2 完成 | paper-advisor | 全文连贯性、学术规范、引用一致性 | PASS / REVISE / DISCUSS |
| M4 | Phase 3 (+3.5) 完成 | paper-advisor | 排版质量、AIGC风险、最终完整性 | PASS / REVISE / DISCUSS |

### 2.3 审查 Agent 规格

| Agent | 职责 | 被谁调用 |
|-------|------|---------|
| **paper-advisor** | 里程碑决策（唯一批准者）| 各 Phase 结束时 |
| **paper-content-reviewer** | 逻辑、结构、范围、学术严谨性 | literature-agent, researcher, copilot, formatter |
| **paper-data-auditor** | 数据一致性、完备性、捏造检测 | researcher, copilot, formatter |

---

## 三、Phase 0 — 订单提炼

### 入口条件
- 用户提供了论文需求（任意形式：图片/PDF/Word/Excel/文本/口头描述）

### 执行 Agent
**paper-order-analyst**

### 步骤

```
Step 0.1  收集原始资料
  → 用户将所有资料平铺放入 00_订单信息/原始资料/（不限格式、不分类）
  → AI 扫描所有文件，逐一识别类型：
    a. 格式模板 → 复制到 01_格式模板/，用 analyze_docx_template 分析
    b. 需求文件 → 提取关键信息（字数、截止日期、格式要求）
    c. 参考范文 → 标记，供 Phase 1a 文献检索参考
    d. 数据文件 → 复制到 02_工作素材/raw/ 或 photos/
    e. 其他 → 标记，保留在原始资料/
  → 生成 00_订单信息/原始资料/README.md（分类清单）
  → 用户不需要手动分子目录或写 README

Step 0.2  分析模板（如果用户提供了格式模板）
  → 调用 analyze_docx_template(template_path)
  → 输出：模板结构报告（样式名、字体、分节、边距）

Step 0.3  提炼订单摘要
  → 从原始资料中提取：
    - 论文标题（或候选标题）
    - 论文类型（毕业论文/期刊/课程）
    - 学科领域
    - 字数要求
    - 截止日期
    - 特殊要求（实验数据、图表数量、引用格式）
  → 写入 00_订单信息/订单摘要.md
  → 格式：YAML frontmatter + Markdown 表格

Step 0.4  提炼格式规范
  → 从模板分析 + 用户要求中提取：
    - 页面设置（纸张大小、边距、行距）
    - 字体要求（正文、标题、摘要 各自字体/字号）
    - 引用格式（GB/T 7714 / APA / IEEE / ...）
    - 图表规范（编号方式、标题位置、分辨率）
    - 章节结构要求
  → 写入 00_订单信息/格式规范.md
  → ★ 高校模板中的值优先级最高，覆盖本规范 Schema 的默认示例值
  → 如果用户额外提出模板之外的要求（如"参考文献用 APA"），叠加记录

Step 0.5  初始化项目目录
  → 创建 00-06 标准目录
  → 将模板文件复制到 01_格式模板/
  → 生成 03_计划与方案/论文撰写计划输入.md
```

### 门控检查

```
Gate 0.1  content-reviewer 审查订单摘要
  → 所有必填字段完整？
  → 论文类型和学科领域明确？
  → 字数要求有具体数字？

Gate 0.2  content-reviewer 审查格式规范
  → 所有格式类别都有具体要求？
  → 引用格式标准明确？
  → 模板分析结果与实际模板一致？
```

### 出口产物

| 文件 | 内容 |
|------|------|
| `00_订单信息/订单摘要.md` | 论文基本信息的结构化表格 + 验证结果 |
| `00_订单信息/格式规范.md` | 按类别分段的完整格式要求 |
| `03_计划与方案/论文撰写计划输入.md` | 供 Phase 1b researcher 使用的输入文件 |
| 标准 00-06 目录 | 空目录就绪 |
| `01_格式模板/*.docx` | 目标格式模板 |

---

## 四、Phase 1a — 文献检索（与 Phase 1b 并行）

### 入口条件
- Phase 0 完成（订单摘要 + 格式规范已就绪）

### 执行 Agent
**paper-literature-agent**

### 步骤

```
Step 1a.1  确定检索策略
  → 从订单摘要提取关键词（中英文）
  → 确定检索源：
    - 中文：知网(CNKI)、万方、百度学术
    - 英文：arXiv、Google Scholar、Semantic Scholar、Web of Science
    - 其他：用户指定的特定来源
  → 确定检索范围（时间、领域、文献类型）
  → 输出：检索策略（写入 literature_cards/_检索策略.md）

Gate 1a.1  content-reviewer 审查检索策略
  → 关键词覆盖研究主题的主要方面？
  → 中英文检索词都有？
  → 检索源足够全面？

Step 1a.2  执行检索
  → 对每个检索源执行检索
  → 去重（按标题/DOI）
  → 初筛：阅读标题+摘要，排除不相关
  → 得到候选文献列表

Step 1a.3  获取全文
  → PDF 优先，CAJ 备用
  → 无法获取全文的标记为「仅有摘要」

Step 1a.4  生成索引卡
  → 对每篇候选文献，阅读全文并生成索引卡
  → 文件命名：{第一作者姓氏}_{年份}.md
  → 放入 04_参考文献/literature_cards/

  每张索引卡格式：
    # {标题}
    **作者**: {完整作者列表}
    **年份**: {YYYY}
    **来源**: {期刊/会议/预印本}
    **DOI/URL**: {链接}
    **cite_key**: {作者}_{年份}
    **关键词**: {3-7 个关键词}

    ## 核心发现 (200-300字)
    {研究问题 + 方法 + 主要发现 + 结论}

    ## 研究方法 (100-200字)
    {实验设计、数据来源、样本量、分析方法}

    ## 与本文关系
    {可以被本文引用在哪一章、什么用途}

Gate 1a.2  content-reviewer 审查索引卡质量
  → 每张卡片的核心发现和研究方法都有实质内容？
  → DOI/URL 字段不为空（或已标记为无法获取）？
  → 「与本文关系」字段有具体说明而非泛泛而谈？
  → 索引卡数量 ≥ 最低要求？（本科≥15，硕士≥30）
```

### 出口产物

| 文件 | 内容 |
|------|------|
| `04_参考文献/literature_cards/{作者}_{年份}.md` × N | 文献索引卡 |
| `04_参考文献/literature_cards/_索引卡汇总.md` | 所有索引卡的汇总表格 |

---

## 五、Phase 1b — 研究规划（与 Phase 1a 并行）

### 入口条件
- Phase 0 完成 + Phase 1a 至少完成到「检索策略已确认」

### 执行 Agent
**paper-researcher**

### 步骤

```
Step 1b.1  文献综合分析（阶段A）
  → 阅读 Phase 1a 产出的索引卡
  → 识别研究缺口（哪些问题已有答案、哪些尚未解决）
  → 确定本文的方法选择
  → 整理相关工作中的关键对比点

Gate 1b.G1  content-reviewer 审查文献基础
  → 文献覆盖了研究主题的核心方向？
  → 研究缺口分析有实质内容？
  → 方法选择有文献支撑？

Step 1b.2  开题报告（阶段B）
  → 撰写开题报告：研究背景 → 研究问题 → 文献综述概要 → 研究方法 → 预期贡献
  → 写入 03_计划与方案/开题报告.md

Gate 1b.G2  content-reviewer 审查学术严谨性
  → 研究问题表述清晰可验证？
  → 方法描述有可操作性？
  → 预期贡献不过度夸大？

Gate 1b.M1  paper-advisor 方向确认 ← M1 里程碑
  → 选题可行性、文献基础、资源可用性
  → 判定: PASS / REVISE / DISCUSS
  → REVISE: 回到对应步骤修改后重新提交
  → 记录到 03_计划与方案/导师确认态.md

Step 1b.3  骨架规划（阶段C）
  → 生成极细骨架大纲（细化到每个自然段的内容要点）
  → 骨架格式：章 → 节 → 小节 → 段落要点 (每个要点 20-30 字)
  → 写入 03_计划与方案/骨架大纲.md

Step 1b.4  核心论点摘要
  → 用 200 字以内概括全文核心论点
  → 写入 03_计划与方案/核心论点摘要.md

Gate 1b.G3  content-reviewer + data-auditor 联合审查
  → content-reviewer: 各章节之间有逻辑递进？覆盖了所有研究问题？
  → data-auditor: 骨架中引用的数据点有来源？没有声称不存在的数据？

Gate 1b.G4  content-reviewer 结构连贯性审查
  → 章与章之间过渡自然？
  → 论点发展有清晰的逻辑链？

Gate 1b.M2  paper-advisor 骨架确认 ← M2 里程碑
  → 研究问题、方法论、框架逻辑、复杂度
  → 判定: PASS / REVISE / DISCUSS
  → 记录到 03_计划与方案/导师确认态.md
```

### 出口产物

| 文件 | 内容 |
|------|------|
| `03_计划与方案/开题报告.md` | 完整开题报告 |
| `03_计划与方案/骨架大纲.md` | 细化到段落级别的完整大纲 |
| `03_计划与方案/核心论点摘要.md` | 200字以内核心论点 |
| `03_计划与方案/导师确认态.md` | M1 + M2 的判定记录 |

---

## 六、Phase 2 — 逐章撰写

### 入口条件
- Phase 1a + Phase 1b 均已完成
- M1 + M2 均为 PASS
- 骨架大纲 + 索引卡 + data_facts 全部就绪

### 执行 Agent
**paper-copilot**

### 步骤（对每一章循环执行）

```
Step 2.1  章节计划确认
  → 从骨架大纲中提取本章的段落要点
  → 列出本章需要的：
    - 引用哪些文献索引卡（cite_key 列表）
    - 使用哪些数据事实（query_data_facts 查询）
    - 生成哪些图表（如有）
  → 写入本章计划（可作为章节文件头部注释）

Gate 2.1  content-reviewer 章节计划审查
  → 本章与前后章节有明确衔接？
  → 引用的文献和数据已就绪？

Step 2.2  逐段撰写
  → 按照骨架大纲的段落要点，逐一撰写
  → 每段撰写时：
    a. search_blocks(keywords) 检索相关索引卡内容
    b. query_data_facts(query) 查询实验数据
    c. 撰写学术文本（保持学术语气、逻辑严密、引用规范）
  → 使用 [cite_key] 格式标记引用位置
  → 每写完一节，保存到 05_撰写过程/第N章_{标题}.md

Step 2.3  更新引用注册表
  → 每章写完后，更新 05_撰写过程/_引用编号注册表.md
  → 注册表格式：
    | 引用编号 | cite_key | 首次出现章节 | 用途说明 |
  → 确保同一文献在全文中的引用编号一致

Gate 2.2  章节质量审查（确定性检查）
  → validate_word_count(chapter_path) — 字数在目标范围内？
  → validate_chapter_citations(chapter_path) — 引用标记正确？
  → content-reviewer: 逻辑连贯、结构清晰、学术严谨
  → data-auditor: 数据准确、来源可查、未捏造
  → 不通过 → REVISE（最多 2 轮）→ 重新执行 Step 2.2

Step 2.4  用户确认
  → 提交章节给用户审阅
  → 用户反馈 → 修改 → 重新确认
  → 确认后锁定本章，进入下一章
```

### 全章撰写完毕后

```
Step 2.5  章节合并
  → 将所有 第N章_{标题}.md 按顺序拼接
  → 生成 05_撰写过程/正文草稿.md
  → 确保：章节编号连续、引用编号全局一致、图表编号连续

Gate 2.3  合并后全局检查
  → validate_word_count(正文草稿.md) — 总字数达标？
  → validate_citations(正文草稿.md) — 所有引用都有对应索引卡？
  → content-reviewer: 全文逻辑连贯、学术规范
  → data-auditor: 全文数据一致性（同一数据在不同章节中一致？）

Gate 2.M3  paper-advisor 草稿审查 ← M3 里程碑
  → 全文连贯性、学术规范、引用一致性
  → 判定: PASS / REVISE / DISCUSS
  → 记录到 03_计划与方案/导师确认态.md
```

### 出口产物

| 文件 | 内容 |
|------|------|
| `05_撰写过程/第N章_{标题}.md` × N | 各章节终稿 |
| `05_撰写过程/正文草稿.md` | 合并后的全量草稿 |
| `05_撰写过程/_引用编号注册表.md` | 引用追踪表 |

---

## 七、Phase 3 — 排版终审

### 入口条件
- Phase 2 完成
- M3 = PASS
- 正文草稿.md + 格式规范.md + 格式模板 + 引用注册表 + 文献索引卡 全部就绪

### 执行 Agent
**paper-formatter**

### 步骤

```
Step 3.1  Markdown 就绪性检查（Gate 1a，并行）
  并行执行以下 4 项检查：
  → validate_markdown_structure(正文草稿.md)
    - 检查：标题层级、列表格式、代码块闭合、表格语法
  → validate_assets(正文草稿.md)
    - 检查：引用的图片路径存在、图片格式可识别
  → validate_word_count(正文草稿.md)
    - 检查：总字数在要求范围内
  → validate_citations(正文草稿.md)
    - 检查：所有 [cite_key] 都有对应索引卡

Step 3.2  引用生成与排序（Gate 1b，串行）
  → build_reference_list(literature_cards目录, 引用格式)
    - 从索引卡汇总中提取所有被引用的文献
    - 按引用格式（GB/T 7714 / APA / IEEE）生成参考文献列表
    - 按引用顺序排列
  → validate_citation_order(正文草稿, 参考文献列表)
    - 验证引用编号与文献列表一一对应
  → 将参考文献列表追加到正文草稿末尾
  → 生成 06_最终交付/正文草稿_含参考文献.md

Step 3.3  排版（Step 2，100% 代码管道）
  → run_format_pipeline(source=正文草稿_含参考文献.md,
                         template=格式模板.docx,
                         output=论文标题_草稿版.docx)
  管道内部逻辑：
    a. apply_minimax_c2（首选）— 使用 minimax-docx 的 C-2 排版链
       - 分节、页眉页脚、目录生成、样式映射、图表嵌入
    b. apply_pandoc_templated（备用）— 如果 C-2 不可用
       - 使用 pandoc + 参考模板生成 docx
    c. 输出 docx 文件

Gate 3.2  DOCX 成品校验（Gate 2）
  并行执行以下 5 项检查：
  → validate_docx_styles — 样式名和定义与模板一致
  → validate_docx_sections — 分节符、页码正确
  → validate_docx_layout — 边距、行距、页眉页脚
  → validate_docx_fonts — 字体嵌入、中英文混排
  → validate_docx_references — 参考文献格式正确
  → 不通过的项 → 修复后重新排版

Step 3.4  终审（Step 3）
  → content-reviewer: 排版后的文档内容完整、可读
  → data-auditor: 排版过程未引入数据错误
  → assess_aigc_risk: AIGC 风险评估

  如果 assess_aigc_risk 返回高风险：
    → 触发 Phase 3.5（降AI处理）
    → 降AI完成后返回此处重新执行 Step 3.4

Gate 3.M4  paper-advisor 交付确认 ← M4 里程碑
  → 排版质量、AIGC风险、最终完整性
  → 判定: PASS / REVISE / DISCUSS
  → PASS 后项目进入 REVIEW 状态，等待用户最终确认
```

### 出口产物

| 文件 | 内容 |
|------|------|
| `06_最终交付/Markdown就绪性报告.md` | Gate 1a 的所有检查结果 |
| `06_最终交付/正文草稿_含参考文献.md` | 正文 + 格式化的参考文献列表 |
| `06_最终交付/{论文标题}_终稿.docx` | 排版完成的最终 docx |
| `06_最终交付/终审报告.md` | content-reviewer + data-auditor 的终审结果 |
| `06_最终交付/排版历程报告.md` | 排版管道执行日志 |

---

## 八、Phase 3.5 — 降AI处理（条件触发）

### 入口条件
- Phase 3 Step 3.4 中 `assess_aigc_risk` 返回高风险
- 或用户显式要求降AI处理

### 执行 Skill
**skills/anti-aigc/** → 详见该 skill 的 SKILL.md

### 步骤概要

```
AIGC-Phase 1  检测基线
  → 多检测器并行评分（GPTZero / Originality / 知网）
  → 生成逐段AI热力图
  → 标记高危段落（AI分 > 阈值）

AIGC-Phase 2  生成层对抗（可选项）
  → 对高危段落用对抗性 Prompt 重新生成
  → 调整解码参数（temperature / top_p）

AIGC-Phase 3  后处理层对抗
  → 阶1: 统计特征多样化（词频分布、句长方差）
  → 阶2: 句式结构变异（主动/被动转换、从句重组）
  → 阶3: 段落结构重组（逻辑链重排、过渡句重写）

AIGC-Phase 4  迭代验证
  → 重新执行 assess_aigc_risk
  → 仍不通过的段落 → 标记 → 二次处理
  → 循环直到全部通过或达到最大迭代次数（3轮）

AIGC-Phase 5  输出
  → 语义保真度验证（改写后原文意思不变？）
  → 生成降AI分析报告
  → 替换 06_最终交付/ 中的 docx
```

### 出口产物

| 文件 | 内容 |
|------|------|
| `06_最终交付/{论文标题}_终稿.docx` | 降AI后的终稿（替换原版） |
| `06_最终交付/降AI处理报告.md` | 处理过程 + 前后对比 + 检测分数变化 |

---

## 九、管线状态转换规则

```
INIT ──(scaffold.sh)──→ ACTIVE

ACTIVE:
  Phase 0 完成 → 进入 Phase 1a + 1b
  Phase 1a + 1b 均完成 + M1+M2=PASS → 进入 Phase 2
  Phase 2 完成 + M3=PASS → 进入 Phase 3
  Phase 3 + (Phase 3.5 可选) 完成 + M4=PASS → 进入 REVIEW

REVIEW:
  用户确认 → 触发 tools/archive.sh → ARCHIVED
  用户提出修改 → 回到对应的 Phase

任一环节 M = REVISE:
  回到对应步骤修改 → 重新提交 advisor → 直到 PASS

任一环节 M = DISCUSS:
  暂停，等待用户决策
```

---

## 十、质量底线（不可跳过的检查）

| 阶段 | 底线检查 | 不通过后果 |
|------|---------|-----------|
| Phase 0 | 订单摘要所有字段完整 | 禁止进入 Phase 1 |
| Phase 1a | 索引卡数量 ≥ 最低要求 | 禁止进入 Phase 2 |
| Phase 1b | M1 + M2 均为 PASS | 禁止进入 Phase 2 |
| Phase 2 | 每章字数在目标范围内 | 该章 REVISE |
| Phase 2 | 所有引用可追溯到索引卡 | 禁止进入 Phase 3 |
| Phase 3 | 所有 DOCX 校验通过 | 修复后重新排版 |
| Phase 3 | AIGC 风险分 < 阈值 | 触发 Phase 3.5 |
