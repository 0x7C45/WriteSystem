# Paper Agents — WriteSystem Agent 使用指南

> 版本: v1.0.0 | 适用于: WriteSystem 论文撰写工作流

---

## WriteSystem Agent 架构

WriteSystem 提供 **8 个核心 Agent** 负责论文撰写管线的各个阶段。

```
Phase 0          Phase 1a/1b        Phase 2           Phase 3          Phase 3.5
订单提炼     →   文献+规划     →   逐章撰写     →   排版终审     →   降AI(条件)
    ↓                ↓                 ↓                 ↓                 ↓
order-analyst   literature      copilot          formatter        anti-aigc
                researcher                                          (skill)
    ↓                ↓                 ↓                 ↓
               M1: advisor        M3: advisor      M4: advisor
               M2: advisor
```

---

## 核心 Agents (8 个)

### 1. paper-order-analyst
- **阶段**: Phase 0
- **职责**: 订单提炼、资料分类、目录初始化
- **输入**: `00_订单信息/原始资料/` 下的所有文件
- **输出**: 订单摘要、格式规范、分类清单
- **何时调用**: 项目启动后，第一步
- **调用方式**: 
  ```
  使用 paper-order-analyst Agent，分析 projects/my-paper/
  ```

### 2. paper-literature-agent
- **阶段**: Phase 1a（与 1b 并行）
- **职责**: 文献检索、索引卡生成
- **输入**: 订单摘要中的关键词和学科领域
- **输出**: `04_参考文献/literature_cards/` 索引卡（本科≥15，硕士≥30）
- **MCP 工具**: `get_literature_cards`, `build_reference_list`, `search_blocks`
- **何时调用**: Phase 0 完成后
- **调用方式**:
  ```
  使用 paper-literature-agent Agent，执行文献检索
  ```

### 3. paper-researcher
- **阶段**: Phase 1b（与 1a 并行）
- **职责**: 文献综合分析、开题报告、骨架规划
- **输入**: Phase 1a 的索引卡
- **输出**: 开题报告、骨架大纲（细化到段落级别）、核心论点摘要
- **依赖**: paper-content-reviewer, paper-data-auditor, paper-advisor
- **何时调用**: Phase 1a 至少完成检索策略后
- **调用方式**:
  ```
  使用 paper-researcher Agent，执行研究规划
  ```

### 4. paper-copilot
- **阶段**: Phase 2
- **职责**: 逐章撰写，引用文献和数据
- **输入**: 骨架大纲、索引卡、data_facts
- **输出**: 各章草稿、正文草稿、引用注册表
- **MCP 工具**: `search_blocks`, `query_data_facts`, `validate_word_count`, `validate_chapter_citations`
- **依赖**: paper-content-reviewer, paper-data-auditor, paper-advisor
- **何时调用**: Phase 1a + 1b 完成且 M1/M2 通过后
- **调用方式**:
  ```
  使用 paper-copilot Agent，开始逐章撰写
  ```

### 5. paper-formatter
- **阶段**: Phase 3
- **职责**: 排版终审、DOCX 生成、AIGC 风险评估
- **输入**: 正文草稿、格式规范、格式模板、索引卡
- **输出**: 最终 DOCX、各类校验报告
- **MCP 工具**: 全部 23 个工具（validate_*, run_format_pipeline, assess_aigc_risk 等）
- **依赖**: paper-content-reviewer, paper-data-auditor, paper-advisor, anti-aigc (skill)
- **何时调用**: Phase 2 完成且 M3 通过后
- **调用方式**:
  ```
  使用 paper-formatter Agent，执行排版终审
  ```

### 6. paper-advisor
- **阶段**: M1-M4 里程碑审查
- **职责**: 唯一的里程碑批准者
- **审查内容**:
  - M1: 选题可行性、文献基础
  - M2: 研究问题、方法论、框架逻辑
  - M3: 全文连贯性、学术规范、引用一致性
  - M4: 排版质量、AIGC风险、最终完整性
- **判定**: PASS / REVISE / DISCUSS
- **何时调用**: 各 Phase 完成后自动触发
- **调用方式**: 自动调用，不需要手动

### 7. paper-content-reviewer
- **阶段**: 全阶段（跨阶段审查）
- **职责**: 逻辑、结构、范围、学术严谨性审查
- **MCP 工具**: `validate_markdown_structure`, `validate_citations`, `validate_word_count`
- **被谁调用**: literature-agent, researcher, copilot, formatter
- **调用时机**: 各 Gate 检查点
- **调用方式**: 自动调用，不需要手动

### 8. paper-data-auditor
- **阶段**: 全阶段（跨阶段审查）
- **职责**: 数据一致性、完备性、捏造检测
- **MCP 工具**: `query_data_facts`, `search_blocks`
- **被谁调用**: researcher, copilot, formatter
- **调用时机**: 涉及数据的 Gate 检查点
- **调用方式**: 自动调用，不需要手动

---

## Agent 调用原则

### 自动调用 vs 手动调用

**自动调用（推荐）**：
```bash
# 一句话启动，AI 自动按顺序调用所有 Agent
bash scripts/run.sh ~/Desktop/论文资料 --auto
```

**手动调用（逐步控制）**：
```
# Phase 0
使用 paper-order-analyst Agent，分析 projects/my-paper/

# Phase 1a
使用 paper-literature-agent Agent，执行文献检索

# Phase 1b
使用 paper-researcher Agent，执行研究规划

# Phase 2
使用 paper-copilot Agent，开始逐章撰写

# Phase 3
使用 paper-formatter Agent，执行排版终审
```

### Agent 依赖关系

```
paper-order-analyst (独立)
    ↓
paper-literature-agent (独立)
paper-researcher
    ├── depends_on: paper-content-reviewer
    ├── depends_on: paper-data-auditor
    └── depends_on: paper-advisor
    ↓
paper-copilot
    ├── depends_on: paper-content-reviewer
    ├── depends_on: paper-data-auditor
    └── depends_on: paper-advisor
    ↓
paper-formatter
    ├── depends_on: paper-content-reviewer
    ├── depends_on: paper-data-auditor
    ├── depends_on: paper-advisor
    └── depends_on: anti-aigc (skill)
```

**跨阶段 Agents**：
- `paper-content-reviewer` — 被 literature-agent, researcher, copilot, formatter 调用
- `paper-data-auditor` — 被 researcher, copilot, formatter 调用
- `paper-advisor` — 在 M1, M2, M3, M4 里程碑自动触发

---

## MCP 工具使用

所有 Agent 都可以访问 `paper-tools-mcp` 提供的 23 个工具：

### 校验工具 (11 个)
- `validate_word_count` — 字数统计
- `validate_citations` — 引用格式检查
- `validate_chapter_citations` — 章节引用检查
- `validate_citation_order` — 引用顺序检查
- `validate_markdown_structure` — Markdown 结构检查
- `validate_assets` — 资源文件检查
- `validate_docx_styles` — DOCX 样式检查
- `validate_docx_sections` — DOCX 分节检查
- `validate_docx_layout` — DOCX 布局检查
- `validate_docx_fonts` — DOCX 字体检查
- `validate_docx_references` — DOCX 参考文献检查

### 排版工具 (4 个)
- `run_format_pipeline` — 排版管道
- `build_preflight_docx` — 预检 DOCX
- `apply_minimax_c2` — MiniMax C-2 排版链
- `apply_pandoc_templated` — Pandoc 模板排版

### 文献工具 (2 个)
- `get_literature_cards` — 获取文献索引卡
- `build_reference_list` — 生成参考文献列表

### 检索工具 (2 个)
- `search_blocks` — 检索索引卡内容
- `query_data_facts` — 查询数据事实

### 其他工具 (4 个)
- `assess_aigc_risk` — AIGC 风险评估
- `query_excel_data` — 查询 Excel 数据
- `validate_excel_formulas` — 校验 Excel 公式
- `analyze_docx_template` — 分析 DOCX 模板

---

## 常见问题

### Q1: 如何知道当前应该调用哪个 Agent？
A: 查看当前 Phase：
- Phase 0 完成 → paper-literature-agent + paper-researcher
- Phase 1a+1b 完成 + M1/M2 通过 → paper-copilot
- Phase 2 完成 + M3 通过 → paper-formatter

### Q2: 可以跳过某个 Agent 吗？
A: 不推荐。每个 Agent 负责特定的质量门控，跳过可能导致后续 Phase 失败。

### Q3: Agent 调用失败怎么办？
A: 
1. 检查依赖的 MCP 工具是否可用
2. 检查输入文件是否就绪
3. 查看错误日志，确定是哪个 Gate 失败
4. 修复后重新调用该 Agent

### Q4: 如何并行调用多个 Agent？
A: Phase 1a 和 1b 可以并行：
```
同时启动：
1. paper-literature-agent — 文献检索
2. paper-researcher — 研究规划（在文献检索到一定数量后开始）
```

### Q5: Advisor 返回 REVISE 怎么办？
A:
- `revise_mode: auto` → AI 自动回到对应步骤修改
- `revise_mode: manual` → 暂停，等待你修改或提供指导

---

## 参考文档

- **完整管线规范** → `spec/conventions/pipeline-spec.md`
- **Agent 定义** → `tools/agent/*.md`
- **MCP 工具** → `tools/mcp-servers/paper-tools-mcp/MANIFEST.yml`
- **工作流指南** → `docs/WORKFLOW_GUIDE.md`
- **一句话启动** → `docs/ONE_COMMAND_WORKFLOW.md`
