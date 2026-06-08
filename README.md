# WriteSystem

论文撰写工作流共享基础设施仓库。所有 AI Agent 平台的单一事实源。

## 一句话启动完整工作流 ⚡

从资料文件夹到最终 DOCX，一条命令搞定：

```bash
bash scripts/run.sh ~/Desktop/论文资料 --auto
```

**支持两种模式**：
- `--auto` — 全自动，AI 一路执行到完成（仅在订单确认和交付时停止）
- `--review` — 中途审查，每个 Phase 结束后暂停汇报

**详细说明** → [`docs/ONE_COMMAND_WORKFLOW.md`](docs/ONE_COMMAND_WORKFLOW.md)

---

## 架构

```
WriteSystem/tools/        ← 通用资源（Git 跟踪）
  agent/ skills/ rules/ mcp-servers/
       ↓ 各 Agent 安装到本地
~/.opencode/  ~/.hermes/  ~/.claude/
```

## 传统手动流程

如果需要逐步手动控制每个阶段：

```bash
# 1. 创建项目
bash scripts/scaffold.sh my-paper

# 2. 手动投放资料到 projects/my-paper/00_订单信息/原始资料/

# 3. 告诉 AI 执行各个 Phase
# Phase 0 → Phase 1a/1b → Phase 2 → Phase 3 → (Phase 3.5)
```

**手动流程指南** → [`docs/QUICKSTART.md`](docs/QUICKSTART.md)

---

## 核心组件

| 组件       | 路径                   |
| -------- | -------------------- |
| 规范       | `spec/` (9 份)        |
| Agent 定义 | `tools/agent/`       |
| Skills   | `tools/skills/`      |
| Rules    | `tools/rules/`       |
| MCP 工具   | `tools/mcp-servers/` |
| 脚本       | `scripts/`           |
| 文献       | `library/`           |
| 文档       | `docs/`              |
| 项目       | `projects/`          |

## 脚本工具

| 脚本 | 功能 |
|------|------|
| `scripts/run.sh` | **一句话启动完整工作流** |
| `scripts/scaffold.sh` | 创建新项目脚手架 |
| `scripts/validate.sh` | 仓库健康检查 |
| `scripts/archive.sh` | 归档完成的项目 |
| `scripts/tool.sh` | 工具注册管理 |

---

## 文档导航

- **快速上手** → [`docs/ONE_COMMAND_WORKFLOW.md`](docs/ONE_COMMAND_WORKFLOW.md) — 一句话启动
- **手动流程** → [`docs/QUICKSTART.md`](docs/QUICKSTART.md) — 5分钟手动流程
- **完整工作流** → [`docs/WORKFLOW_GUIDE.md`](docs/WORKFLOW_GUIDE.md) — 详细工作流说明
- **管线规范** → [`spec/conventions/pipeline-spec.md`](spec/conventions/pipeline-spec.md) — Phase 0-3.5 完整规范
- **配置说明** → [`spec/conventions/pipeline-config.md`](spec/conventions/pipeline-config.md) — interaction_level 和 revise_mode
- **Agent 职责** → [`AGENTS.md`](AGENTS.md) — Agent 入口文档

---

## 快速示例

### 全自动模式（推荐）

```bash
# 准备材料文件夹
mkdir ~/论文资料
cp ~/Desktop/*.{pdf,docx,xlsx,jpg} ~/论文资料/

# 一句话启动
bash scripts/run.sh ~/论文资料 --auto

# AI 会提示你在 Agent 中执行指令
# 然后 AI 自动执行全部 Phase，3-8小时后生成最终 DOCX
```

### 中途审查模式

```bash
# 每个 Phase 结束后停止，向你汇报进展
bash scripts/run.sh ~/论文资料 --review
```

### 指定格式模板

```bash
bash scripts/run.sh ~/论文资料 --auto --template ~/学位论文模板.docx
```

---

## 仓库状态

✅ **迁移完成** — 所有核心组件已就位
✅ **架构完整** — Phase 0-3.5 全流程自动化
✅ **健康检查通过** — 0 错误, 0 警告

运行健康检查：
```bash
bash scripts/validate.sh
```
