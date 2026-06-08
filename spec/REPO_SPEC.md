# WriteSystem 仓库规范

> 版本: v1.0.0 | 最后更新: 2026-06-04

---

## 一、仓库定位

WriteSystem 是**论文撰写工作流的共享基础设施仓库**。所有 AI Agent 平台的**单一事实源**。

## 二、目录结构

```
WriteSystem/
├── AGENTS.md                ← Agent 通用入口
│
├── spec/                    ← 仓库规范
│   ├── REPO_SPEC.md
│   ├── VERSION
│   ├── conventions/
│   └── changelog/
│
├── tools/                   ← 通用工具资源
│   ├── agent/               ← Agent 定义
│   ├── skills/              ← Skill 定义
│   ├── rules/               ← 规则定义
│   └── mcp-servers/         ← MCP 工具服务
│
├── scripts/                 ← 仓库管理脚本
│   ├── scaffold.sh
│   ├── archive.sh
│   └── validate.sh
│
├── library/                 ← 共享文献库
├── docs/                    ← 仓库级文档
├── projects/                ← 论文项目实例
│   └── _archive/
│
├── .gitignore
└── README.md
```

## 三、项目生命周期

```
INIT → ACTIVE → REVIEW → ARCHIVED
```

```bash
bash scripts/scaffold.sh {project_name}   # 创建
bash scripts/archive.sh {project_name}    # 归档
```

## 四、核心约定

| 约定 | 详见 |
|------|------|
| 文件命名 | `conventions/file-naming.md` |
| 原始资料与素材管理 | `conventions/source-materials.md` |
| 项目生命周期 + 归档协议 | `conventions/project-lifecycle.md` |
| 论文撰写管线流程 | `conventions/pipeline-spec.md` |
| 质量标准与工具契约 | `conventions/quality-and-tools.md` |
| 文件格式 Schema | `conventions/file-schemas.md` |
| 审查规则细则 | `conventions/review-rules.md` |
| **管线交互配置** | `conventions/pipeline-config.md` |
| **工具出入与替换** | `conventions/tool-registry.md` |
| Git 提交规范 + 分支策略 | `conventions/git-strategy.md` |
| 跨 Agent 兼容 | `conventions/cross-agent.md` |

## 五、快速开始

### 一句话启动（推荐）

```bash
# 将所有参考文件放到一个文件夹，一条命令启动
bash scripts/run.sh ~/Desktop/论文资料 --auto
```

详见 `docs/ONE_COMMAND_WORKFLOW.md`

### 传统手动流程

```bash
cat spec/REPO_SPEC.md                     # 阅读规范
bash scripts/scaffold.sh my-paper         # 创建项目
# 投放资料到 projects/my-paper/00_订单信息/原始资料/
# 告诉 AI "开始执行 Phase 0"
bash scripts/validate.sh                  # 健康检查
bash scripts/archive.sh my-paper          # 归档项目
```

详见 `docs/QUICKSTART.md`

> 任何 Agent 进入此仓库，应先阅读 `AGENTS.md` 和本文件。
