#!/bin/bash
# scaffold.sh — 创建新论文项目脚手架
# 用法: bash scripts/scaffold.sh {project_name}

set -euo pipefail

if [ $# -eq 0 ]; then
    echo "用法: bash scripts/scaffold.sh {project_name}"
    echo "示例: bash scripts/scaffold.sh writing3"
    exit 1
fi

PROJECT_NAME="$1"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_DIR="$REPO_ROOT/projects/$PROJECT_NAME"

if [ -d "$PROJECT_DIR" ]; then
    echo "错误: 项目 '$PROJECT_NAME' 已存在: $PROJECT_DIR"
    exit 1
fi

echo "创建项目: $PROJECT_NAME"
echo "位置: $PROJECT_DIR"
echo ""

# ── 创建目录结构 ──
# 原始资料/ — 平铺，不分子目录（用户直接扔文件，AI 负责分类）
mkdir -p "$PROJECT_DIR/00_订单信息/原始资料"
mkdir -p "$PROJECT_DIR/01_格式模板"
mkdir -p "$PROJECT_DIR/02_工作素材"/{scripts,raw,charts,photos}
mkdir -p "$PROJECT_DIR/03_计划与方案"
mkdir -p "$PROJECT_DIR/04_参考文献/literature_cards"
mkdir -p "$PROJECT_DIR/05_撰写过程"
mkdir -p "$PROJECT_DIR/06_最终交付"
mkdir -p "$PROJECT_DIR/_REVIEWS"

SPEC_VERSION=$(cat "$REPO_ROOT/spec/VERSION" 2>/dev/null || echo "unknown")
TODAY=$(date +%Y-%m-%d)

# ── 原始资料 README（AI 日后填充） ──
cat > "$PROJECT_DIR/00_订单信息/原始资料/README.md" << EOF
# 原始资料清单

> 项目: $PROJECT_NAME | 自动生成: $TODAY
> 将由 paper-order-analyst 在 Phase 0 扫描后自动更新

## 格式模板

(Phase 0 时 AI 自动识别并复制到 01_格式模板/)

## 需求文件

(Phase 0 时 AI 自动识别并分类)

## 参考范文

(Phase 0 时 AI 自动识别并分类)

## 附件

(Phase 0 时 AI 自动识别并分类)

## 用户笔记

(Phase 0 时 AI 自动识别并分类)

## 数据文件

(Phase 0 时 AI 自动识别并复制到 02_工作素材/)
EOF

# ── 里程碑审查报告目录 ──
cat > "$PROJECT_DIR/_REVIEWS/README.md" << EOF
# 里程碑审查报告

> 项目: $PROJECT_NAME | 创建时间: $TODAY

本目录存放 paper-advisor Agent 的里程碑审查报告，其他 Agent 禁止读取。

## 里程碑审查

| 里程碑 | 报告文件 | 审查内容 | 执行时机 |
|--------|---------|---------|---------|
| M1: 方向确认 | M1_方向确认.md | 选题可行性、文献基础、资源可用性 | Phase 1b 开题报告完成后 |
| M2: 骨架确认 | M2_骨架确认.md | 研究问题、方法论、框架逻辑、复杂度 | Phase 1b 骨架大纲完成后 |
| M3: 草稿审查 | M3_草稿审查.md | 全文连贯性、学术规范、引用一致性 | Phase 2 正文草稿完成后 |
| M4: 交付确认 | M4_交付确认.md | 排版质量、AIGC风险、最终完整性 | Phase 3 最终DOCX生成后 |

## 审查报告格式

每个审查报告包含：
- 审查结果（PASS / REVISE / DISCUSS）
- 审查维度评分
- 具体问题清单
- 修改建议
- 导师确认态更新（M1/M2）

## 工作区隔离

**重要**: 为确保审查独立性，其他 Agent 禁止读取本目录。
- paper-order-analyst: ❌ 禁止读取
- paper-literature-agent: ❌ 禁止读取
- paper-researcher: ❌ 禁止读取
- paper-copilot: ❌ 禁止读取
- paper-formatter: ❌ 禁止读取
- paper-advisor: ✅ 唯一可写入本目录的 Agent

审查报告仅在用户确认时展示，不泄露到其他 Agent 的上下文中。
EOF

# ── 订单摘要 ──
cat > "$PROJECT_DIR/00_订单信息/订单摘要.md" << EOF
---
repo_spec_version: $SPEC_VERSION
project_version: 1
created: $TODAY
status: active
pipeline:
  interaction_level: coarse     # coarse | fine | minimal
  revise_mode: auto             # auto | manual
  max_revise_rounds: 2
---

# 订单摘要

> 项目: $PROJECT_NAME | 创建: $TODAY

## 基本信息

| 字段 | 值 |
|------|-----|
| 论文标题 | (待填写) |
| 类型 | (毕业论文 / 期刊论文 / 课程论文) |
| 学科领域 | (待填写) |
| 字数要求 | (待填写) |
| 截止日期 | (待填写) |
| 引用格式 | (GB/T 7714 / APA / IEEE) |

## 特殊要求

(如：实验数据、图表数量下限、英文摘要等)
EOF

# ── 格式规范 ──
cat > "$PROJECT_DIR/00_订单信息/格式规范.md" << EOF
# 格式规范

> 项目: $PROJECT_NAME | 模板位置: \`01_格式模板/\`
> 将由 paper-order-analyst 在 Phase 0 分析模板后自动填写

## 页面设置
| 项目 | 值 |
|------|-----|
| 纸张大小 | (待分析) |
| 页边距 | (待分析) |
| 行距 | (待分析) |

## 字体要求
| 元素 | 字体 | 字号 | 加粗 | 对齐 |
|------|------|------|------|------|
| 正文 | (待分析) | | | |

## 引用格式
- 标准: (待分析)
EOF

# ── data_facts ──
cat > "$PROJECT_DIR/02_工作素材/data_facts.md" << EOF
# 实验数据摘要

> 项目: $PROJECT_NAME | 最后更新: $TODAY
> 数据采集方法: (问卷 / 实验 / 仿真 / 文献提取)

## 数据集 1: (名称)
**来源**: (待填写) | **样本量**: N = (待填写)

| 变量 | 均值 | 标准差 | 最小值 | 最大值 | N |
|------|------|--------|--------|--------|---|
| (待填写) | | | | | |

### 关键发现
1. (待填写)
EOF

# ── 占位 ──
touch "$PROJECT_DIR/02_工作素材/scripts/.gitkeep"
touch "$PROJECT_DIR/02_工作素材/raw/.gitkeep"
touch "$PROJECT_DIR/02_工作素材/charts/.gitkeep"
touch "$PROJECT_DIR/02_工作素材/photos/.gitkeep"

echo ""
echo "✓ 项目 '$PROJECT_NAME' 创建完成"
echo ""
echo "目录结构:"
find "$PROJECT_DIR" -type d | sed "s|$PROJECT_DIR|  $PROJECT_NAME|" | sort
echo ""
echo "下一步:"
echo "  1. 将所有资料（PDF/DOCX/图片/MD/任意格式）扔进 00_订单信息/原始资料/"
echo "  2. 不需要分类，AI 会自动识别和归类"
echo "  3. 运行 Phase 0，AI 会生成分类清单和订单摘要"
