# WriteSystem — Agent Operating Manual

> 所有 AI Agent 进入此仓库时，首先阅读本文件。

## What This Repo Is

论文撰写工作流的共享基础设施仓库。所有 Agent 平台（OpenCode / Hermes / Claude Code / Codex）的**单一事实源**。

## 架构原则

```
WriteSystem/              ← 通用资源层（Git 跟踪）
  tools/
    agent/   skills/   rules/   mcp-servers/
       ↓ 各 Agent 安装到本地
~/.opencode/  ~/.hermes/  ~/.claude/   ← 平台专属（Git 忽略）
```

## How To Navigate

### 必读

1. `spec/REPO_SPEC.md` — 仓库规范主文档
2. `spec/conventions/` — 全部约定（10 份规范）

### 通用资源

| 目录 | 内容 |
|------|------|
| `tools/agent/` | Agent 定义（通用格式） |
| `tools/skills/` | Skill 定义 |
| `tools/rules/` | 规则定义 |
| `tools/mcp-servers/` | MCP 工具服务 |
| `library/` | 共享文献库 |
| `docs/` | 仓库级文档 |

### 项目与工具

| 目录 | 内容 |
|------|------|
| `projects/` | 论文项目实例 |
| `scripts/` | 仓库工具脚本 |

## Rules For All Agents

### 必须遵守

1. **不修改 `projects/_archive/`** — 已归档项目只读
2. **不在项目根目录放置临时文件** — 脚本放 `02_工作素材/scripts/`
3. **不保留编译产物** — `__pycache__/`, `bin/`, `obj/`, `*.pyc`, `*.dll`, `*.pdb` 不入库
4. **一个终稿原则** — `06_最终交付/` 中只保留一个终稿 docx
5. **模板不重复** — 模板文件只在 `01_格式模板/` 中存在一份
6. **不创建平台专属目录** — `.opencode/` `.hermes/` `.claude/` 不在仓库中

### 安装到本地

各 Agent 平台从仓库安装到自己的本地目录：

```
OpenCode:   tools/agent/ → ~/.opencode/agents/
            tools/skills/ → ~/.opencode/skills/
            tools/rules/  → ~/.opencode/rules/

Hermes:     tools/agent/ → ~/.hermes/agents/
            tools/skills/ → ~/.hermes/skills/
            tools/rules/  → ~/.hermes/rules/
```

### 用户操作流程

#### 方式 1: 一句话启动（推荐）

```bash
# 将所有参考文件放到一个文件夹
bash scripts/run.sh ~/Desktop/论文资料 --auto
# AI 自动执行全部 Phase 0-3.5，3-8小时后生成最终 DOCX
```

**详细文档** → `docs/ONE_COMMAND_WORKFLOW.md`

#### 方式 2: 传统手动流程

```
用户:  bash scripts/scaffold.sh my-paper
用户:  把所有资料扔进 projects/my-paper/00_订单信息/原始资料/
用户:  告诉 AI "开始执行 Phase 0"
AI:    逐个 Phase 执行（按 pipeline-config 的交互粒度暂停）
```

**详细文档** → `docs/QUICKSTART.md`

### 项目目录结构速查

```
projects/{name}/
├── 00_订单信息/       ← 需求定义（含原始资料/平铺投放点）
├── 01_格式模板/       ← 目标格式模板（AI 自动识别放入）
├── 02_工作素材/       ← 原始数据/图表/代码
├── 03_计划与方案/     ← 开题/大纲/论点
├── 04_参考文献/       ← 文献索引卡
├── 05_撰写过程/       ← 逐章草稿
├── 06_最终交付/       ← 终稿+报告
└── 07_归档快照/       ← 归档摘要
```

## 论文管线 Agent 角色

| Agent | 阶段 | 职责 |
|-------|------|------|
| paper-order-analyst | Phase 0 | 订单提炼、目录初始化、原始资料自动分类 |
| paper-literature-agent | Phase 1a | 文献检索、索引卡生成 |
| paper-researcher | Phase 1b | 文献综合、开题、骨架规划 |
| paper-copilot | Phase 2 | 逐章撰写 |
| paper-formatter | Phase 3 | 排版与终审 |
| paper-advisor | M1-M4 | 里程碑审查 |
| paper-content-reviewer | 全阶段 | 逻辑/结构/学术审查 |
| paper-data-auditor | 全阶段 | 数据一致性/捏造检测 |
