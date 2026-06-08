# 跨 Agent 兼容性约定

> 版本: v1.0.0 | 所属: WriteSystem spec/conventions

---

## 架构原则

## 通用入口文件

`AGENTS.md`（根目录）是**所有 Agent 平台的统一入口**。

Agent 进入仓库时按以下顺序读取：
1. `AGENTS.md` — 导航 + 规则
2. `spec/REPO_SPEC.md` — 完整规范
3. `spec/conventions/*.md` — 按需加载

## 各 Agent 平台的安装方式

### OpenCode

```bash
ln -s $(pwd)/tools/agent  ~/.opencode/agents
ln -s $(pwd)/tools/skills ~/.opencode/skills
ln -s $(pwd)/tools/rules  ~/.opencode/rules
```

### Hermes

```bash
# Hermes 自动读取根目录 AGENTS.md
ln -s $(pwd)/tools/skills ~/.hermes/skills/writesystem
```

### Claude Code

```bash
# Claude Code 自动读取根目录 AGENTS.md
ln -s $(pwd)/tools/agent ~/.claude/agents/
```

## Agent 定义的通用格式

```markdown
---
name: paper-copilot
description: 论文写作 Agent
phase: 2
tools: [search_blocks, query_data_facts, ...]
---

# paper-copilot
## 职责 / 工作流程 / 门控检查
```

各平台安装时转换 frontmatter 为自己的格式。

## 仓库中不存在的目录（.gitignore）

- `.opencode/` — OpenCode 本地
- `.hermes/` — Hermes 本地
- `.claude/` — Claude Code 本地
- `CLAUDE.md` — Claude Code 专属
