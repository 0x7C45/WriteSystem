# QUICKSTART.md — 5 分钟快速上手

> WriteSystem 论文撰写工作流 | 版本: v1.0.0

从零创建你的第一个论文项目，5 分钟内启动全自动撰写管线。

**🚀 寻找更简单的方式？** 查看 [一句话启动完整工作流](ONE_COMMAND_WORKFLOW.md) — 一条命令从资料到 DOCX

---

## 前置要求

### 必需
- **Python 3.8+** — 用于数据处理和 MCP 服务
- **Bash** — 脚本执行环境（Linux/macOS/WSL）
- **AI Agent 平台** — 以下任一：
  - OpenCode
  - Hermes
  - Claude Code
  - Codex

### 可选（提升体验）
- **Git** — 版本追踪（推荐）
- **Word/LibreOffice** — 预览终稿 docx
- **Pandoc** — 备用排版引擎（当 minimax-docx 不可用时）

---

## Step 1: 创建项目

在 WriteSystem 根目录下运行：

```bash
bash scripts/scaffold.sh my-paper
```

**输出示例**：
```
创建项目: my-paper
位置: /path/to/WriteSystem/projects/my-paper

✓ 项目 'my-paper' 创建完成

目录结构:
  my-paper
  my-paper/00_订单信息
  my-paper/00_订单信息/原始资料
  my-paper/01_格式模板
  my-paper/02_工作素材
  my-paper/03_计划与方案
  my-paper/04_参考文献
  my-paper/05_撰写过程
  my-paper/06_最终交付
```

**生成了什么**：
- 标准 00-06 目录结构（符合 `spec/conventions/` 规范）
- `00_订单信息/订单摘要.md` — 预填充模板
- `00_订单信息/格式规范.md` — 预填充模板
- `00_订单信息/原始资料/README.md` — AI 稍后自动更新

---

## Step 2: 投放原始资料

**关键原则**：平铺投放，无需分类，AI 自动识别。

将以下**所有**资料扔进 `projects/my-paper/00_订单信息/原始资料/`：

| 资料类型 | 示例 | AI 自动处理 |
|---------|------|------------|
| **格式模板** | `学位论文模板.docx` | 复制到 `01_格式模板/`，分析样式 |
| **需求文件** | `论文要求.pdf`, `任务书.txt` | 提取字数、截止日期、格式要求 |
| **参考范文** | `往届范文.pdf` | 标记，供文献检索参考 |
| **数据文件** | `实验数据.xlsx`, `调查问卷.csv` | 复制到 `02_工作素材/raw/` |
| **图片附件** | `实验照片.jpg`, `流程图.png` | 复制到 `02_工作素材/photos/` |
| **用户笔记** | `我的想法.md`, `研究问题.txt` | 保留在原始资料，提取关键信息 |
| **其他** | 任何格式 | 标记类型，保留待查 |

**无需**：
- ❌ 手动创建子目录（如 `需求/`, `模板/`）
- ❌ 重命名文件（AI 识别内容，不依赖文件名）
- ❌ 编写 README（AI 扫描后自动生成分类清单）

**投放完成后的示例**：
```
00_订单信息/原始资料/
├── 毕业论文格式模板.docx
├── 论文任务书.pdf
├── 实验数据-2023.xlsx
├── 参考范文-张三-2022.pdf
├── 我的研究问题.txt
└── README.md  ← AI 稍后更新
```

---

## Step 3: 启动 Phase 0 — 订单提炼

告诉你的 AI Agent：

```
开始分析项目 my-paper，执行 Phase 0
```

或者（如果 AI 支持角色切换）：

```
使用 paper-order-analyst Agent，分析 projects/my-paper/
```

**Phase 0 自动执行**：
1. **扫描原始资料**（Step 0.1）
   - 识别每个文件的类型
   - 模板文件 → `analyze_docx_template` 分析样式
   - 数据文件 → 移动到 `02_工作素材/`
   - 更新 `原始资料/README.md` 分类清单

2. **提炼订单摘要**（Step 0.3）
   - 提取：论文标题、类型、学科、字数、截止日期
   - 写入 `00_订单信息/订单摘要.md`

3. **提炼格式规范**（Step 0.4）
   - 从模板提取：页边距、字体、行距、引用格式
   - 写入 `00_订单信息/格式规范.md`

4. **质量门控**（Gate 0.1 + 0.2）
   - `paper-content-reviewer` 审查完整性
   - 不通过 → AI 自动修复 → 重新提交

**预期耗时**：2-5 分钟（取决于资料数量）

**Phase 0 完成标志**：
```
✓ 订单摘要已生成
✓ 格式规范已提炼
✓ 原始资料已分类
→ 准备进入 Phase 1a + 1b
```

---

## Step 4: 检查 Phase 0 产物（可选）

Phase 0 完成后，检查以下文件确认 AI 理解正确：

### 4.1 检查订单摘要
```bash
cat projects/my-paper/00_订单信息/订单摘要.md
```

**期望内容**：
```markdown
---
repo_spec_version: v1.0.0
project_version: 1
created: 2026-06-06
status: active
pipeline:
  interaction_level: coarse
  revise_mode: auto
  max_revise_rounds: 2
---

# 订单摘要

| 字段 | 值 |
|------|-----|
| 论文标题 | （AI 提取的标题） |
| 类型 | 毕业论文 / 期刊论文 / 课程论文 |
| 学科领域 | （具体领域） |
| 字数要求 | 8000-10000 |
| 截止日期 | 2026-07-15 |
| 引用格式 | GB/T 7714 |
```

### 4.2 检查格式规范
```bash
cat projects/my-paper/00_订单信息/格式规范.md
```

**期望内容**：
- 页面设置（A4、边距 2.5cm）
- 字体要求（正文宋体小四、标题黑体三号）
- 引用格式（具体标准）

### 4.3 检查资料分类
```bash
cat projects/my-paper/00_订单信息/原始资料/README.md
```

**期望内容**：
- 格式模板清单（含文件名 + 分析状态）
- 需求文件清单
- 数据文件清单
- 附件清单

**如果发现错误**：
```
请修正订单摘要中的截止日期为 2026-08-01
```

---

## Step 5: 后续流程概览

Phase 0 完成后，管线自动进入后续阶段：

### Phase 1a — 文献检索（并行）
**Agent**: `paper-literature-agent`
**时长**: 30-60 分钟
**产物**: 
- `04_参考文献/literature_cards/{作者}_{年份}.md` × N
- `04_参考文献/literature_cards/_索引卡汇总.md`

**做什么**：
- 根据论文主题检索中英文文献（知网、Google Scholar、arXiv）
- 为每篇文献生成索引卡（核心发现、研究方法、与本文关系）
- 至少 15 篇（本科）或 30 篇（硕士）

### Phase 1b — 研究规划（并行）
**Agent**: `paper-researcher`
**时长**: 30-60 分钟
**产物**:
- `03_计划与方案/开题报告.md`
- `03_计划与方案/骨架大纲.md` — **细化到每个段落的 20-30 字要点**
- `03_计划与方案/核心论点摘要.md`

**里程碑**：
- **M1 (方向确认)** — Phase 1a 完成后，`paper-advisor` 审查选题可行性
- **M2 (骨架确认)** — Phase 1b 完成后，`paper-advisor` 审查研究问题和方法论

### Phase 2 — 逐章撰写
**Agent**: `paper-copilot`
**时长**: 2-6 小时（取决于字数）
**产物**:
- `05_撰写过程/第N章_{标题}.md` × N
- `05_撰写过程/正文草稿.md` — 合并后全文
- `05_撰写过程/_引用编号注册表.md`

**做什么**：
- 按骨架大纲逐段撰写
- 自动引用索引卡内容（`search_blocks`）
- 自动查询实验数据（`query_data_facts`）
- 每章完成后质量门控（字数、引用格式、逻辑连贯性）

**里程碑**：
- **M3 (草稿审查)** — 全文完成后，`paper-advisor` 审查连贯性和学术规范

### Phase 3 — 排版终审
**Agent**: `paper-formatter`
**时长**: 10-30 分钟
**产物**:
- `06_最终交付/{论文标题}_终稿.docx`
- `06_最终交付/Markdown就绪性报告.md`
- `06_最终交付/终审报告.md`

**做什么**：
- 验证 Markdown 结构（标题层级、引用格式）
- 生成参考文献列表（按引用顺序）
- 使用 `minimax-docx` 或 `pandoc` 排版成 docx
- 校验样式、分节、页码、字体

**里程碑**：
- **M4 (交付确认)** — `paper-advisor` 最终审查

### Phase 3.5 — 降AI处理（条件触发）
**Skill**: `skills/anti-aigc/`
**时长**: 20-40 分钟
**触发条件**: `assess_aigc_risk` 返回高风险

**做什么**：
- 多检测器评分（GPTZero / Originality / 知网）
- 对高危段落进行统计特征多样化、句式变异、段落重组
- 迭代验证直到通过（最多 3 轮）

---

## 管线配置（高级）

调整 `00_订单信息/订单摘要.md` 头部的 `pipeline` 段控制交互频率：

```yaml
pipeline:
  interaction_level: coarse     # 粗粒度（默认）— AI 每个 Phase 结束后暂停
  # interaction_level: fine     # 细粒度 — AI 每写完一章暂停确认
  # interaction_level: minimal  # 最小化 — AI 一路跑到交付，只在里程碑暂停

  revise_mode: auto             # 自动修订（默认）— AI 自动修复门控不通过项
  # revise_mode: manual         # 手动修订 — AI 报告问题，等待你修改

  max_revise_rounds: 2          # 自动修订最大轮数
```

---

## 常见问题

### Q1: 我没有格式模板怎么办？
**A**: 没关系！AI 会使用默认学术论文格式（A4、宋体小四、1.5 倍行距、GB/T 7714 引用）。你也可以在 Phase 0 后手动编辑 `00_订单信息/格式规范.md`。

### Q2: 我只有口头需求，没有文件怎么办？
**A**: 在 `00_订单信息/原始资料/` 创建 `需求描述.txt`，写下你的要求（任意格式），AI 会提取。

### Q3: Phase 0 识别错了文件类型怎么办？
**A**: 告诉 AI：
```
请将 data.xlsx 移动到 02_工作素材/raw/，它是实验数据
```

### Q4: 里程碑审查不通过 (REVISE) 怎么办？
**A**: AI 会自动回到对应步骤修改，重新提交 `paper-advisor`。如果你不同意修改方向：
```
请保留原研究问题，只调整文献综述部分
```

### Q5: 我想手动写某一章怎么办？
**A**: 在 Phase 2 时告诉 AI：
```
第 3 章我自己写，跳过它，继续第 4 章
```
然后手动创建 `05_撰写过程/第3章_xxx.md`，AI 合并时会包含它。

### Q6: 终稿 AIGC 风险高怎么办？
**A**: Phase 3 会自动触发 Phase 3.5 降AI处理。如果你想跳过：
```
跳过降AI处理，我接受当前版本
```

---

## 下一步

- **深入规范** → 阅读 `spec/conventions/pipeline-spec.md`（完整管线规范）
- **Agent 定义** → 阅读 `tools/agent/*.md`（了解每个 Agent 的能力）
- **质量工具** → 阅读 `spec/conventions/quality-and-tools.md`（MCP 工具使用）
- **归档协议** → 阅读 `spec/conventions/project-lifecycle.md`（项目归档规则）

---

## 故障排除

### Phase 0 卡住不动
```bash
# 检查原始资料是否为空
ls -la projects/my-paper/00_订单信息/原始资料/

# 手动触发
bash scripts/validate.sh  # 验证项目结构
```

### AI 找不到模板
```bash
# 确认模板在正确位置
find projects/my-paper -name "*.docx"

# 如果模板在错误位置，手动移动
mv projects/my-paper/00_订单信息/原始资料/模板.docx \
   projects/my-paper/01_格式模板/
```

### 依赖缺失
```bash
# 检查 Python 版本
python3 --version  # 应该 >= 3.8

# 检查 MCP 服务（如果使用）
ls -la tools/mcp-servers/
```

---

**准备好了？现在创建你的第一个项目**：

```bash
bash scripts/scaffold.sh my-first-paper
# 投放资料到 projects/my-first-paper/00_订单信息/原始资料/
# 告诉 AI: "开始分析项目 my-first-paper，执行 Phase 0"
```